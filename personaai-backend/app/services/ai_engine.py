import re
from sqlalchemy.orm import Session

from app.models.chat_config import ChatConfig
from app.models.conversation import Conversation
from app.models.reply_suggestion import ReplySuggestion
from app.models.tone_profile import ToneProfile
from app.models.chat_tone_profile import ChatToneProfile
from app.schemas.ai import GenerateReplyRequest
from app.services.encryption import EncryptionService
from app.services.mood_detector import MoodDetectorService
from app.services.openai_client import create_chat_completion, parse_json_response
from app.services.chat_history_service import ChatHistoryService
from app.services.intent_detector import IntentDetectorService

from app.services.feedback_processor import FeedbackProcessorService
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
    def detect_mood(cls, message: str) -> str:
        return MoodDetectorService.detect(message)

    @classmethod
    def generate_reply(
        cls,
        db: Session,
        user_id: str,
        message: str,
        chat_config_id: str,
        count: int = 3,
    ) -> list[str]:
        if not message or not message.strip():
            raise ValueError("Incoming message cannot be empty")

        payload = GenerateReplyRequest(
            chat_config_id=chat_config_id,
            incoming_messages=[message],
            conversation_history=[],
            count=count,
        )
        _conversation, suggestions, _detected_mood = cls.generate_replies(db, user_id, payload)
        return [EncryptionService.decrypt(item.reply_text) for item in suggestions]

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
        language_mix = tone_profile.language_mix if tone_profile else []
        avg_message_length = tone_profile.avg_message_length if tone_profile else None
        common_emojis = tone_profile.common_emojis if tone_profile else []
        history_dump = [message.model_dump() for message in payload.conversation_history][-50:]

        # Load chat-specific tone profile
        chat_tone_profile = db.query(ChatToneProfile).filter(
            ChatToneProfile.chat_config_id == chat_config.id
        ).order_by(ChatToneProfile.updated_at.desc()).first()

        # Build chat-specific tone dict for prompt
        chat_tone_dict = None
        if chat_tone_profile:
            chat_tone_dict = {
                "formality_score": chat_tone_profile.formality_score,
                "punctuation_style": chat_tone_profile.punctuation_style,
                "common_emojis": chat_tone_profile.common_emojis,
                "message_openers": chat_tone_profile.message_openers,
                "message_closers": chat_tone_profile.message_closers,
                "avg_message_length": chat_tone_profile.avg_message_length,
            }

        # Load extended chat history from ChatMessageLog
        chat_message_logs = ChatHistoryService.get_chat_history(db, chat_config.id, limit=100)
        extended_history_dump = []
        if chat_message_logs:
            extended_history_dump = [
                {"role": "user" if log.message_role == "user" else "contact", "text": log.message_text}
                for log in reversed(chat_message_logs)
            ]

        # The client sends the live, two-sided transcript; the stored log only fills in
        # older turns. Replacing one with the other used to hand the model a one-sided
        # conversation with none of the user's own messages in it.
        history_to_use = cls._merge_history(extended_history_dump, history_dump)

        # Detect intent
        detected_intent_obj = IntentDetectorService.detect(payload.incoming_messages, history_to_use)

        # Load feedback patterns
        positive_patterns = FeedbackProcessorService.get_positive_reply_patterns(db, user_id)
        negative_patterns = FeedbackProcessorService.get_negative_reply_patterns(db, user_id)

        prompt = build_reply_prompt(
            incoming_messages=payload.incoming_messages,
            conversation_history=history_to_use,
            personality_mode=chat_config.personality_mode,
            detected_mood=detected_mood,
            slang_patterns=slang_patterns,
            language_mix=language_mix,
            avg_message_length=avg_message_length,
            common_emojis=common_emojis,
            chat_tone_profile=chat_tone_dict,
            global_tone_profile=tone_profile,
            detected_intent=detected_intent_obj.label(),
            positive_examples=positive_patterns,
            negative_examples=negative_patterns,
            count=payload.count,
        )

        conversation = Conversation(
            user_id=user_id,
            chat_config_id=chat_config.id,
            incoming_msg=EncryptionService.encrypt(combined_message),
            detected_mood=detected_mood,
            context_window=history_dump,
        )
        db.add(conversation)
        db.flush()

        # Log the user's own latest turn before the incoming one, so the stored history
        # keeps both sides. Without it the chat tone learner never sees a single user
        # message and the transcript we prompt with reads like a monologue.
        cls._log_latest_user_turn(db, chat_config.id, user_id, history_dump, extended_history_dump)

        # Log the incoming message to chat history
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat_config.id,
            user_id=user_id,
            message_role="contact",
            message_text=combined_message,
            detected_mood=detected_mood,
        )

        # Trigger auto-retrain every 20 messages
        msg_count = ChatHistoryService.get_message_count(db, chat_config.id)
        if msg_count > 0 and msg_count % 20 == 0:
            try:
                from app.workers.training_job import retrain_chat_tone_job
                retrain_chat_tone_job.delay(chat_config.id, user_id)
            except Exception as exc:
                # Retraining is an optional background refinement; a missing or
                # unreachable broker must not fail the caller's reply request.
                print(f"Could not queue chat tone retraining: {exc}")

        reply_texts = []
        if settings.llm_enabled:
            try:
                response = create_chat_completion(
                    model=settings.resolved_chat_model,
                    messages=[
                        {"role": "system", "content": prompt["system"]},
                        {"role": "user", "content": prompt["user"]},
                    ],
                    max_tokens=300,
                    # Small chat models drift off the instructions above ~0.8; this keeps
                    # the replies varied without letting them wander off context.
                    temperature=0.7,
                    top_p=0.9,
                )

                if response and response.choices:
                    response_text = response.choices[0].message.content
                    reply_texts = cls._extract_reply_texts(response_text, payload.count)
                    reply_texts = cls._drop_echoed_replies(reply_texts, combined_message)
            except Exception as e:
                print(f"Failed to fetch replies from {settings.normalized_llm_provider}: {e}")
        
        if not reply_texts:
            fallback_replies = cls._fallback_replies(
                message=combined_message,
                conversation_history=history_dump,
                detected_mood=detected_mood,
                personality_mode=chat_config.personality_mode,
                language_mix=language_mix,
                count=payload.count,
            )
            reply_texts = fallback_replies
        elif len(reply_texts) < payload.count:
            fallback_replies = cls._fallback_replies(
                message=combined_message,
                conversation_history=history_dump,
                detected_mood=detected_mood,
                personality_mode=chat_config.personality_mode,
                language_mix=language_mix,
                count=payload.count,
            )
            for fallback_text in fallback_replies:
                if fallback_text not in reply_texts:
                    reply_texts.append(fallback_text)
                if len(reply_texts) >= payload.count:
                    break

        # Re-rank replies based on feedback patterns
        reply_texts = cls._rerank_replies(reply_texts, positive_patterns, negative_patterns)

        # Encrypt replies for storage
        suggestions = [
            ReplySuggestion(
                conversation_id=conversation.id,
                reply_text=EncryptionService.encrypt(text),
                rank=i + 1,
            )
            for i, text in enumerate(reply_texts[:payload.count])
        ]
        
        for suggestion in suggestions:
            db.add(suggestion)

        db.commit()
        db.refresh(conversation)
        for suggestion in suggestions:
            db.refresh(suggestion)

        return conversation, suggestions, detected_mood

    @staticmethod
    def _normalize_message_text(text: object) -> str:
        return " ".join(str(text or "").split()).lower()

    @classmethod
    def _merge_history(
        cls,
        stored_history: list[dict[str, str]],
        client_history: list[dict[str, str]],
        limit: int = 40,
    ) -> list[dict[str, str]]:
        """Combine the stored log with the transcript the client just sent.

        The client window is the live tail of the chat and is the only source that
        carries the user's own messages, so it always wins; stored messages only add
        older turns the client did not include.
        """
        if not client_history:
            return stored_history[-limit:]
        if not stored_history:
            return client_history[-limit:]

        client_keys = {
            (message.get("role"), cls._normalize_message_text(message.get("text")))
            for message in client_history
        }
        older = [
            message
            for message in stored_history
            if (message.get("role"), cls._normalize_message_text(message.get("text"))) not in client_keys
        ]
        return (older + client_history)[-limit:]

    @classmethod
    def _log_latest_user_turn(
        cls,
        db: Session,
        chat_config_id: str,
        user_id: str,
        client_history: list[dict[str, str]],
        stored_history: list[dict[str, str]],
    ) -> None:
        latest_user_text = next(
            (
                message.get("text")
                for message in reversed(client_history)
                if message.get("role") == "user" and str(message.get("text", "")).strip()
            ),
            None,
        )
        if not latest_user_text:
            return

        already_stored = {
            cls._normalize_message_text(message.get("text"))
            for message in stored_history
            if message.get("role") == "user"
        }
        if cls._normalize_message_text(latest_user_text) in already_stored:
            return

        try:
            ChatHistoryService.log_message(
                db=db,
                chat_config_id=chat_config_id,
                user_id=user_id,
                message_role="user",
                message_text=" ".join(str(latest_user_text).split()),
            )
        except Exception as exc:
            # History logging is best-effort context enrichment, never a reason to
            # fail the reply the caller is waiting on.
            print(f"Could not log user message to chat history: {exc}")

    @classmethod
    def _rerank_replies(cls, replies: list[str], positive_patterns: list[str], negative_patterns: list[str]) -> list[str]:
        if not positive_patterns and not negative_patterns:
            return replies

        def score_reply(reply: str) -> float:
            score = 0.0
            reply_lower = reply.lower()
            
            for pattern in positive_patterns:
                words = [w for w in pattern.lower().split() if len(w) > 3]
                for w in words:
                    if w in reply_lower:
                        score += 1.0
                        
            for pattern in negative_patterns:
                words = [w for w in pattern.lower().split() if len(w) > 3]
                for w in words:
                    if w in reply_lower:
                        score -= 1.0
                        
            return score

        return sorted(replies, key=score_reply, reverse=True)

    # Preambles a small chat model adds around the replies. Left in place they get
    # served to the user as if they were reply options.
    META_LINE_PATTERN = re.compile(
        r"^(here (are|is)|here's|below (are|is)|these are|sure[,!]? here|okay[,!]? here|"
        r"as requested|based on|i hope this|hope this helps|let me know if|note that|note:|"
        r"reply options|options:|replies:)",
        re.IGNORECASE,
    )

    @staticmethod
    def _extract_reply_texts(raw_replies: object, count: int) -> list[str]:
        # The prompt asks for one reply per line, so only pay for a JSON parse (and its
        # failure warning) when the model actually answered with JSON.
        parsed_replies = (
            parse_json_response(raw_replies)
            if AIEngineService._looks_like_json(raw_replies)
            else None
        )
        if isinstance(parsed_replies, dict):
            reply_list = parsed_replies.get("replies", [])
        elif isinstance(parsed_replies, list):
            reply_list = parsed_replies
        else:
            reply_list = AIEngineService._extract_reply_lines(str(raw_replies or ""))

        clean_replies = []
        for reply in reply_list:
            text = AIEngineService._clean_reply_text(str(reply))
            if not text or AIEngineService._is_meta_text(text):
                continue
            if text not in clean_replies:
                clean_replies.append(text)
            if len(clean_replies) >= count:
                break
        if clean_replies:
            return clean_replies

        return AIEngineService._extract_reply_strings_from_broken_json(str(raw_replies or ""), count)

    @staticmethod
    def _looks_like_json(raw_replies: object) -> bool:
        if isinstance(raw_replies, dict | list):
            return True
        candidate = str(raw_replies or "").strip().strip("`").strip()
        return candidate.removeprefix("json").strip().startswith(("{", "["))

    @staticmethod
    def _clean_reply_text(text: str) -> str:
        """Strip the list markers, speaker labels and quotes models wrap replies in."""
        cleaned = " ".join(str(text or "").split())
        cleaned = re.sub(r"^(?:[-*•]|\d+[.)])\s*", "", cleaned)
        cleaned = re.sub(r"^(?:reply|option|me|you)\s*\d*\s*[:\-]\s+", "", cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip().strip("`").strip()
        if len(cleaned) >= 2 and cleaned[0] in "\"'“‘" and cleaned[-1] in "\"'”’":
            cleaned = cleaned[1:-1].strip()
        return cleaned

    @staticmethod
    def _is_meta_text(text: str) -> bool:
        if AIEngineService.META_LINE_PATTERN.match(text):
            return True
        # A short line ending in a colon is a heading, not a text someone would send.
        return text.endswith(":") and len(text.split()) <= 8

    @staticmethod
    def _drop_echoed_replies(replies: list[str], incoming_message: str) -> list[str]:
        """Discard options that just parrot the incoming message back."""
        incoming = " ".join(str(incoming_message or "").split()).lower().strip(" .!?")
        if not incoming:
            return replies
        return [reply for reply in replies if reply.lower().strip(" .!?") != incoming]

    @staticmethod
    def _extract_reply_lines(content: str) -> list[str]:
        lines = []
        for line in str(content or "").splitlines():
            cleaned = AIEngineService._clean_reply_text(line)
            if cleaned.lower().startswith("replies:"):
                cleaned = cleaned.split(":", 1)[1].strip()
            if cleaned:
                lines.append(cleaned)
        return lines

    @staticmethod
    def _extract_reply_strings_from_broken_json(content: str, count: int) -> list[str]:
        matches = re.findall(r'"([^"\n]{2,160})"', content)
        clean_replies = []
        for match in matches:
            text = " ".join(match.split())
            if text.lower() == "replies":
                continue
            if text and text not in clean_replies:
                clean_replies.append(text)
            if len(clean_replies) >= count:
                break
        return clean_replies

    @classmethod
    def _fallback_replies(
        cls,
        message: str,
        conversation_history: list[dict[str, str]],
        detected_mood: str,
        personality_mode: str | None,
        language_mix: list[str] | None,
        count: int,
    ) -> list[str]:
        cleaned = cls._clean_context(message)
        detected_mood = cls._fallback_mood(message, detected_mood)
        language = cls._infer_reply_language(message, conversation_history, language_mix or [])
        templates = cls._fallback_templates(detected_mood, personality_mode, language)
        replies = []
        for template in templates:
            reply = template.format(message=cleaned).strip()
            if reply and reply not in replies:
                replies.append(reply)
            if len(replies) >= count:
                break
        return replies[:count]

    @staticmethod
    def _fallback_templates(detected_mood: str, personality_mode: str | None, language: str) -> list[str]:
        if language == "Hindi":
            return AIEngineService._fallback_templates_hindi(detected_mood, personality_mode)
        if language == "Hinglish":
            return AIEngineService._fallback_templates_hinglish(detected_mood, personality_mode)

        if detected_mood == "romantic":
            return [
                "I miss you too.",
                "Love you too.",
                "Aww, that made me smile.",
                "Come here, I miss you more.",
                "You are too sweet.",
            ]

        if detected_mood == "curious":
            return [
                "Tell me a little more.",
                "What do you mean exactly?",
                "Wait, explain that once.",
                "I am listening.",
                "Can you send one more detail?",
            ]

        if detected_mood == "concerned":
            return [
                "I get it. Give me a minute.",
                "Do not worry, I will handle it.",
                "Let me check and get back to you.",
                "I understand. We will sort this out.",
                "Okay, I am on it.",
            ]

        if detected_mood == "happy":
            return [
                "Haha nice.",
                "That sounds good.",
                "I am in.",
                "Love that.",
                "Perfect, let us do it.",
            ]

        if personality_mode == "serious":
            return [
                "Sure, I will get back to you.",
                "Understood. I will check and reply.",
                "Sounds good.",
                "Okay, noted.",
                "Give me a moment, please.",
            ]

        if personality_mode == "savage":
            return [
                "Bold of you to say that.",
                "That is a plot twist.",
                "Noted, with dramatic effect.",
                "Okay, that was unexpected.",
                "Fair enough.",
            ]

        return [
            "Haha okay.",
            "Give me a minute.",
            "Sounds good.",
            "I will reply properly in a bit.",
            "Okay, done.",
        ]

    @staticmethod
    def _fallback_templates_hinglish(detected_mood: str, personality_mode: str | None) -> list[str]:
        if detected_mood == "romantic":
            return [
                "Aww, miss you too.",
                "Love you yaar.",
                "Tu bahut sweet hai.",
                "Main bhi tujhe miss kar raha tha.",
                "Aaja jaldi, yaad aa rahi thi.",
            ]

        if detected_mood == "curious":
            return [
                "Haan bata, detail mein.",
                "Kya scene hai exactly?",
                "Accha, thoda aur samjha.",
                "Main sun raha hoon, bol.",
                "Ek aur detail bhej na.",
            ]

        if detected_mood == "concerned":
            return [
                "Haan, dekh raha hoon abhi.",
                "Tension mat le, handle kar lunga.",
                "Ek min de, check karke batata hoon.",
                "Samajh gaya, sort karte hain.",
                "Theek hai, main dekh leta hoon.",
            ]

        if personality_mode == "serious":
            return [
                "Theek hai, main check karke batata hoon.",
                "Samajh gaya, thodi der mein reply karta hoon.",
                "Haan, noted.",
                "Okay, dekh leta hoon.",
                "Ek minute do please.",
            ]

        if personality_mode == "savage":
            return [
                "Waah, full plot twist hai.",
                "Bold move yaar.",
                "Theek hai, dramatic tha thoda.",
                "Unexpected tha, but okay.",
                "Fair hai, maan liya.",
            ]

        return [
            "Haan okay.",
            "Ek min, batata hoon.",
            "Scene sahi hai.",
            "Theek hai, karta hoon.",
            "Haan done.",
        ]

    @staticmethod
    def _fallback_templates_hindi(detected_mood: str, personality_mode: str | None) -> list[str]:
        if detected_mood == "romantic":
            return [
                "Main bhi tumhe yaad kar raha tha.",
                "Tum bahut pyaare ho.",
                "Aww, ye sunke accha laga.",
                "Main bhi tumse pyaar karta hoon.",
                "Jaldi milo na.",
            ]

        if detected_mood == "curious":
            return [
                "Thoda aur batao.",
                "Matlab kya hai exactly?",
                "Accha, ek baar detail mein samjhao.",
                "Main sun raha hoon.",
                "Ek aur detail bhejo.",
            ]

        if detected_mood == "concerned":
            return [
                "Theek hai, main dekh raha hoon.",
                "Chinta mat karo, sambhal lenge.",
                "Mujhe ek minute do, check karke batata hoon.",
                "Samajh gaya, isse theek karte hain.",
                "Theek hai, main ispar kaam karta hoon.",
            ]

        if personality_mode == "serious":
            return [
                "Theek hai, main check karke batata hoon.",
                "Samajh gaya. Main jaldi reply karta hoon.",
                "Theek hai, note kar liya.",
                "Main dekh leta hoon.",
                "Kripya ek minute dijiye.",
            ]

        return [
            "Theek hai.",
            "Ek minute, batata hoon.",
            "Accha hai.",
            "Main thodi der mein reply karta hoon.",
            "Ho gaya.",
        ]

    @staticmethod
    def _clean_context(message: str) -> str:
        return " ".join(message.split())[:80].strip()

    @staticmethod
    def _fallback_mood(message: str, detected_mood: str) -> str:
        lowered = message.lower()
        if any(phrase in lowered for phrase in {"miss you", "love you", "i miss", "i love", "ily", "luv"}):
            return "romantic"
        return detected_mood

    @staticmethod
    def _infer_reply_language(
        message: str,
        conversation_history: list[dict[str, str]],
        language_mix: list[str],
    ) -> str:
        combined_text = " ".join(
            [message] + [item.get("text", "") for item in conversation_history[-50:]]
        ).lower()
        has_devanagari = any("\u0900" <= char <= "\u097f" for char in combined_text)
        hindi_markers = {"acha", "achha", "arre", "bhai", "haan", "hai", "kya", "kyu", "kyun", "nahi", "nhi", "theek", "thik", "yaar"}
        marker_count = sum(1 for word in combined_text.split() if word.strip(".,!?") in hindi_markers)

        if has_devanagari:
            return "Hindi"
        if "Hindi" in (language_mix or []) and re.search(r"\b[a-z]+\b", combined_text):
            return "Hinglish"
        if marker_count >= 3:
            return "Hinglish"
        return "English"
