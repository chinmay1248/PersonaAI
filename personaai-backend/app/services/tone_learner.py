from collections import Counter
from datetime import datetime, timezone
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
    SLANG_HINTS = {"bro", "yaar", "ngl", "fr", "lol", "lmao", "brb", "btw", "omg", "nope", "yeah", "sup", "yo"}
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
        
        if settings.openai_enabled and settings.pinecone_api_key:
            try:
                client = openai.OpenAI(api_key=settings.openai_api_key)
                response = client.embeddings.create(
                    input="\\n".join(samples),
                    model="text-embedding-3-small"
                )
                embedding = response.data[0].embedding
                
                pc = Pinecone(api_key=settings.pinecone_api_key)
                index_name = "personaai-tone"
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
        profile.last_trained_at = datetime.now(timezone.utc)

        for sample in samples:
            db.add(TrainingSample(user_id=user_id, sample_text=sample, source="manual", used_in_training=True))

        db.commit()
        db.refresh(profile)
        return profile

    @classmethod
    def train_from_messages(
        cls, db: Session, user_id: str, messages: list[str], source: str = "whatsapp"
    ) -> ToneProfile:
        """
        Continuously train from real chat messages.
        Merges new patterns with existing profile instead of replacing.
        """
        # Get existing profile or create new one
        profile = db.query(ToneProfile).filter(ToneProfile.user_id == user_id).one_or_none()
        
        if not profile:
            # If no profile exists, do initial training with these messages
            return cls.train(db, user_id, messages)

        # Analyze new messages
        words = [word.lower().strip(".,!?") for message in messages for word in message.split()]
        new_slang = sorted({word for word in words if word in cls.SLANG_HINTS})
        emoji_matches = cls.EMOJI_PATTERN.findall(" ".join(messages))
        new_emoji_frequency = len(emoji_matches) / max(len(messages), 1)
        new_avg_length = sum(len(msg.split()) for msg in messages) / len(messages)

        # Merge with existing patterns (weighted average towards new data)
        existing_slang = set(profile.slang_patterns or [])
        merged_slang = sorted(existing_slang.union(new_slang))

        # Update profile with merged data
        # Weight: 70% existing, 30% new (to keep learning but not overwrite everything)
        profile.avg_message_length = (profile.avg_message_length or 0) * 0.7 + new_avg_length * 0.3
        profile.emoji_frequency = (profile.emoji_frequency or 0) * 0.7 + new_emoji_frequency * 0.3
        profile.slang_patterns = merged_slang
        profile.common_emojis = [item for item, _ in Counter(emoji_matches + profile.common_emojis).most_common(5)]
        profile.last_trained_at = datetime.now(timezone.utc)
        
        # Update formality based on slang
        profile.formality_score = max(1.0, min(5.0, 5.0 - (len(merged_slang) * 0.5)))

        # Update embeddings if API keys available
        if settings.openai_enabled and settings.pinecone_api_key:
            try:
                client = openai.OpenAI(api_key=settings.openai_api_key)
                # Use a sample of messages for embedding
                sample_messages = messages[:10] if len(messages) > 10 else messages
                response = client.embeddings.create(
                    input="\\n".join(sample_messages),
                    model="text-embedding-3-small"
                )
                embedding = response.data[0].embedding
                
                pc = Pinecone(api_key=settings.pinecone_api_key)
                index_name = "personaai-tone"
                try:
                    index = pc.Index(index_name)
                    index.upsert(vectors=[(user_id, embedding, {"user_id": user_id})])
                except Exception as e:
                    print(f"Failed to upsert to pinecone: {e}")
            except Exception as e:
                print(f"Failed to generate embeddings: {e}")

        # Save training samples
        for message in messages:
            db.add(TrainingSample(user_id=user_id, sample_text=message, source=source, used_in_training=True))

        # Update accuracy score (increases with more training)
        total_samples = db.query(TrainingSample).filter(
            TrainingSample.user_id == user_id, TrainingSample.used_in_training == True
        ).count()
        profile.accuracy_score = min(0.95, 0.5 + (total_samples / 100.0))

        db.commit()
        db.refresh(profile)
        return profile
