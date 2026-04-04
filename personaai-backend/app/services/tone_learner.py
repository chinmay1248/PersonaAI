from collections import Counter
from datetime import datetime
import re
import json

import openai
from pinecone import Pinecone
from sqlalchemy.orm import Session

from app.models.tone_profile import ToneProfile
from app.models.training_sample import TrainingSample
from app.config import get_settings

settings = get_settings()

class ToneLearnerService:
    SLANG_HINTS = {"bro", "yaar", "ngl", "fr", "lol", "lmao", "brb", "btw"}
    EMOJI_PATTERN = re.compile(r"[\U0001F300-\U0001FAFF]")

    @classmethod
    def train(cls, db: Session, user_id: str, samples: list[str]) -> ToneProfile:
        words = [word.lower().strip(".,!?") for sample in samples for word in sample.split()]
        slang_patterns = sorted({word for word in words if word in cls.SLANG_HINTS})
        emoji_matches = cls.EMOJI_PATTERN.findall(" ".join(samples))
        punctuation_style = "expressive" if any("!" in sample for sample in samples) else "calm"
        caps_usage = "mixed" if any(any(char.isupper() for char in sample) for sample in samples) else "lowercase"
        language_mix = ["English"]

        if any(word in {"yaar", "kya", "hai", "bhai"} for word in words):
            language_mix.append("Hindi")

        avg_message_length = sum(len(sample.split()) for sample in samples) / len(samples)
        emoji_frequency = len(emoji_matches) / max(len(samples), 1)
        formality_score = max(1.0, min(5.0, 5.0 - (len(slang_patterns) * 0.5)))
        
        vector_id = f"local-{user_id}"
        
        if settings.openai_api_key and settings.pinecone_api_key:
            try:
                client = openai.OpenAI(api_key=settings.openai_api_key)
                response = client.embeddings.create(
                    input="\\n".join(samples),
                    model="text-embedding-3-small"
                )
                embedding = response.data[0].embedding
                
                pc = Pinecone(api_key=settings.pinecone_api_key)
                index_name = "personaai-tone"
                # Using a try block since creating index requires checking if it exists, for now we will just assume the index exists and insert
                # Ideally index creation sits in a migration or init script
                try:
                    index = pc.Index(index_name)
                    index.upsert(vectors=[(user_id, embedding, {"user_id": user_id})])
                    vector_id = user_id
                except Exception as e:
                    print(f"Failed to upsert to pinecone: {e}")
            except Exception as e:
                print(f"Failed to generate embeddings: {e}")

        profile = db.query(ToneProfile).filter(ToneProfile.user_id == user_id).one_or_none()
        if not profile:
            profile = ToneProfile(user_id=user_id)
            db.add(profile)

        profile.formality_score = formality_score
        profile.avg_message_length = avg_message_length
        profile.emoji_frequency = emoji_frequency
        profile.common_emojis = [item for item, _ in Counter(emoji_matches).most_common(5)]
        profile.slang_patterns = slang_patterns
        profile.punctuation_style = punctuation_style
        profile.caps_usage = caps_usage
        profile.language_mix = language_mix
        profile.vector_id = vector_id
        profile.last_trained_at = datetime.utcnow()

        for sample in samples:
            db.add(TrainingSample(user_id=user_id, sample_text=sample, source="manual", used_in_training=True))

        db.commit()
        db.refresh(profile)
        return profile
