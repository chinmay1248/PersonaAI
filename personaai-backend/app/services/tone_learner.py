from collections import Counter
from datetime import datetime, timezone
import re

from pinecone import Pinecone
from sqlalchemy.orm import Session

from app.models.tone_profile import ToneProfile
from app.models.training_sample import TrainingSample
from app.models.user import User
from app.config import get_settings
from app.services.openai_client import create_embeddings

settings = get_settings()

class ToneLearnerService:
    SLANG_HINTS = {
        "bro", "yaar", "ngl", "fr", "lol", "lmao", "brb", "btw", "omg", "nope", "yeah", "sup", "yo",
        "lit", "fam", "cap", "fire", "lowkey", "sus", "nah", "yep", "cool"
    }
    EMOJI_PATTERN = re.compile(r"[\U0001F300-\U0001FAFF]")

    @classmethod
    def train(cls, db: Session, user_id: str, samples: list[str]) -> ToneProfile:
        cls._ensure_user_exists(db, user_id)
        samples = cls._normalize_samples(samples)
        slang_patterns = cls._extract_slang_patterns(samples)
        common_emojis, emoji_frequency = cls._extract_emoji_patterns(samples)
        punctuation_style = "expressive" if any("!" in sample for sample in samples) else "calm"
        caps_usage = "mixed" if any(any(char.isupper() for char in sample) for sample in samples) else "lowercase"
        language_mix = cls._detect_language_mix(samples)

        avg_message_length = sum(len(sample.split()) for sample in samples) / len(samples)
        formality_score = max(1.0, min(5.0, cls._analyze_formality(samples) * 5.0))
        
        vector_id = f"local-{user_id}"
        
        if settings.llm_enabled and settings.pinecone_api_key:
            response = create_embeddings(input="\n".join(samples), model=settings.resolved_embedding_model)
            if response and response.data:
                embedding = response.data[0].embedding
                pc = Pinecone(api_key=settings.pinecone_api_key)
                index_name = "personaai-tone"
                try:
                    index = pc.Index(index_name)
                    index.upsert(vectors=[(user_id, embedding, {"user_id": user_id})])
                    vector_id = user_id
                except Exception as e:
                    print(f"Failed to upsert to pinecone: {e}")

        profile = db.query(ToneProfile).filter(ToneProfile.user_id == user_id).one_or_none()
        if not profile:
            profile = ToneProfile(user_id=user_id)
            db.add(profile)

        profile.formality_score = formality_score
        profile.avg_message_length = avg_message_length
        profile.emoji_frequency = emoji_frequency
        profile.common_emojis = common_emojis
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
        cls._ensure_user_exists(db, user_id)
        messages = cls._normalize_samples(messages)

        # Get existing profile or create new one
        profile = db.query(ToneProfile).filter(ToneProfile.user_id == user_id).one_or_none()
        
        if not profile:
            # If no profile exists, do initial training with these messages
            return cls.train(db, user_id, messages)

        # Analyze new messages
        new_slang = cls._extract_slang_patterns(messages)
        new_common_emojis, new_emoji_frequency = cls._extract_emoji_patterns(messages)
        new_avg_length = sum(len(msg.split()) for msg in messages) / len(messages)

        # Merge with existing patterns (weighted average towards new data)
        existing_slang = set(profile.slang_patterns or [])
        merged_slang = sorted(existing_slang.union(new_slang))

        # Update profile with merged data
        # Weight: 70% existing, 30% new (to keep learning but not overwrite everything)
        profile.avg_message_length = (profile.avg_message_length or 0) * 0.7 + new_avg_length * 0.3
        profile.emoji_frequency = (profile.emoji_frequency or 0) * 0.7 + new_emoji_frequency * 0.3
        profile.slang_patterns = merged_slang
        profile.common_emojis = [
            item
            for item, _ in Counter(new_common_emojis + (profile.common_emojis or [])).most_common(5)
        ]
        profile.last_trained_at = datetime.now(timezone.utc)
        
        # Update formality based on slang
        profile.formality_score = max(1.0, min(5.0, 5.0 - (len(merged_slang) * 0.5)))

        # Update embeddings if API keys available
        if settings.llm_enabled and settings.pinecone_api_key:
            sample_messages = messages[:10] if len(messages) > 10 else messages
            response = create_embeddings(input="\n".join(sample_messages), model=settings.resolved_embedding_model)
            if response and response.data:
                embedding = response.data[0].embedding
                pc = Pinecone(api_key=settings.pinecone_api_key)
                index_name = "personaai-tone"
                try:
                    index = pc.Index(index_name)
                    index.upsert(vectors=[(user_id, embedding, {"user_id": user_id})])
                except Exception as e:
                    print(f"Failed to upsert to pinecone: {e}")

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

    @classmethod
    def _ensure_user_exists(cls, db: Session, user_id: str) -> None:
        if not db.get(User, user_id):
            raise ValueError("User not found")

    @classmethod
    def _normalize_samples(cls, samples: list[str]) -> list[str]:
        clean_samples = [sample.strip() for sample in samples if sample and sample.strip()]
        if not clean_samples:
            raise ValueError("At least one non-empty sample is required")
        return clean_samples

    @classmethod
    def _extract_slang_patterns(cls, samples: list[str]) -> list[str]:
        words = [
            word.lower().strip(".,!?;:\"'()[]{}")
            for sample in samples
            for word in sample.split()
        ]
        return sorted({word for word in words if word in cls.SLANG_HINTS})

    @classmethod
    def _extract_emoji_patterns(cls, samples: list[str]) -> tuple[list[str], float]:
        emoji_matches = cls.EMOJI_PATTERN.findall(" ".join(samples))
        common_emojis = [item for item, _ in Counter(emoji_matches).most_common(5)]
        return common_emojis, min(1.0, len(emoji_matches) / max(len(samples), 1))

    @classmethod
    def _analyze_formality(cls, samples: list[str]) -> float:
        informal = set(cls._extract_slang_patterns(samples))
        informal_count = len(informal)
        formal_markers = {
            "appreciate", "inquiry", "regards", "please", "thank", "morning", "afternoon", "certainly"
        }
        words = [word.lower().strip(".,!?;:\"'()[]{}") for sample in samples for word in sample.split()]
        formal_count = sum(1 for word in words if word in formal_markers)
        score = 0.5 + (formal_count * 0.12) - (informal_count * 0.12)
        return max(0.0, min(1.0, score))

    @classmethod
    def _detect_language_mix(cls, samples: list[str]) -> list[str]:
        text = " ".join(samples).lower()
        languages = ["English"]
        if any(word in text for word in {"yaar", "kya", "hai", "bhai", "namaste", "acha"}):
            languages.append("Hindi")
        if any(word in text for word in {"hola", "gracias", "adios"}):
            languages.append("Spanish")
        if re.search(r"[\u0400-\u04FF]", text):
            languages.append("Cyrillic")
        return languages
