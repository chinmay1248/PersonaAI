import json
import openai
from sqlalchemy.orm import Session

from app.models.chat_config import ChatConfig
from app.models.conversation import Conversation
from app.models.reply_suggestion import ReplySuggestion
from app.models.tone_profile import ToneProfile
from app.schemas.ai import GenerateReplyRequest
from app.services.encryption import EncryptionService
from app.services.mood_detector import MoodDetectorService
from app.utils.prompt_builder import build_reply_prompt
from app.config import get_settings

settings = get_settings()

class AIEngineService:
    PERSONALITY_PREFIX = {
        "funny": ["haha", "lol", "bro"],
        "serious": ["Sure", "Understood", "Sounds good"],
        "romantic": ["aw", "hey you", "that sounds sweet"],
        "savage": ["wild", "not gonna lie", "bold move"],
    }

    @classmethod
    def generate_replies(
        cls,
        db: Session,
        user_id: str,
        payload: GenerateReplyRequest,
    ) -> tuple[Conversation, list[ReplySuggestion], str]:
        chat_config = db.get(ChatConfig, payload.chat_config_id)
        if not chat_config or chat_config.user_id != user_id:
            raise ValueError("Chat configuration not found")

        combined_message = " ".join(payload.incoming_messages)
        detected_mood = MoodDetectorService.detect(combined_message)
        tone_profile = db.query(ToneProfile).filter(ToneProfile.user_id == user_id).one_or_none()
        slang_patterns = tone_profile.slang_patterns if tone_profile else []
        
        prompt = build_reply_prompt(
            incoming_messages=payload.incoming_messages,
            personality_mode=chat_config.personality_mode,
            detected_mood=detected_mood,
            slang_patterns=slang_patterns,
        )

        conversation = Conversation(
            user_id=user_id,
            chat_config_id=chat_config.id,
            incoming_msg=EncryptionService.encrypt(combined_message),
            detected_mood=detected_mood,
            context_window=[message.model_dump() for message in payload.conversation_history],
        )
        db.add(conversation)
        db.flush()

        reply_texts = []
        if settings.openai_api_key:
            try:
                client = openai.OpenAI(api_key=settings.openai_api_key)
                system_prompt = f"{prompt['system']} You must provide exactly {payload.count} varied reply options formatted ONLY as a valid JSON array of strings. Do not include markdown formatting. Return JSON like: {{\"replies\": [\"reply 1\", \"reply 2\"]}}"
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt['user']}
                    ],
                    max_tokens=600,
                    temperature=0.8,
                    response_format={"type": "json_object"}
                )
                
                response_text = response.choices[0].message.content
                parsed_replies = json.loads(response_text)
                if isinstance(parsed_replies, dict) and "replies" in parsed_replies:
                    reply_list = parsed_replies["replies"]
                    if isinstance(reply_list, list):
                        reply_texts = [str(r) for r in reply_list[:payload.count]]
            except Exception as e:
                print(f"Failed to fetch from OpenAI: {e}")
        
        # Fallback if no API key or API failed
        if not reply_texts:
            prefixes = cls.PERSONALITY_PREFIX.get(chat_config.personality_mode or "", ["hey", "sure", "okay"])
            for index in range(payload.count):
                prefix = prefixes[index % len(prefixes)]
                reply_texts.append(f"{prefix} {cls._response_body(combined_message, detected_mood, index + 1)}")

        suggestions: list[ReplySuggestion] = []
        for index, text in enumerate(reply_texts):
            suggestion = ReplySuggestion(
                conversation_id=conversation.id,
                reply_text=EncryptionService.encrypt(text),
                rank=index + 1,
            )
            db.add(suggestion)
            suggestions.append(suggestion)

        db.commit()
        db.refresh(conversation)
        for suggestion in suggestions:
            db.refresh(suggestion)

        return conversation, suggestions, detected_mood

    @staticmethod
    def _response_body(message: str, detected_mood: str, variant: int) -> str:
        short_message = message[:60].rstrip()
        if detected_mood == "concerned":
            return f"I saw your message about \"{short_message}\". Let's handle it, option {variant}."
        if detected_mood == "happy":
            return f"that sounds fun about \"{short_message}\". I'm in, option {variant}."
        if detected_mood == "curious":
            return f"about \"{short_message}\", I can reply with more detail, option {variant}."
        return f"for \"{short_message}\", here's a natural reply option {variant}."
