from app.config import get_settings
from app.services.openai_client import create_chat_completion

settings = get_settings()

class MoodDetectorService:
    @classmethod
    def detect(cls, text: str) -> str:
        if not settings.openai_enabled:
            lowered = text.lower()
            if any(word in lowered for word in {"haha", "lol", "great", "nice", "awesome", "fun", "love"}):
                return "happy"
            if any(word in lowered for word in {"sad", "angry", "upset", "bad", "stress", "deadline", "sorry"}):
                return "concerned"
            if "?" in lowered:
                return "curious"
            return "neutral"

        response = create_chat_completion(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a mood classification engine. Read the message and output ONE SINGLE WORD representing the mood. "
                        "Allowed words: happy, sad, angry, excited, neutral, sarcastic, concerned, curious, romantic."
                    ),
                },
                {"role": "user", "content": text[:1000]},
            ],
            max_tokens=10,
            temperature=0.0,
        )

        if not response or not response.choices:
            return "neutral"

        mood = response.choices[0].message.content.strip().lower()
        mood = "".join(c for c in mood if c.isalpha())
        allowed = {"happy", "sad", "angry", "excited", "neutral", "sarcastic", "concerned", "curious", "romantic"}
        return mood if mood in allowed else "neutral"
