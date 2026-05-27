import re
from typing import Optional
from sqlalchemy.orm import Session
from app.models import ChatToneProfile, ChatMessageLog
from app.services.tone_learner import ToneLearnerService
import json


class ChatToneLearnerService:
    """Service for learning and managing per-chat tone profiles."""

    SLANG_HINTS = {
        "bro", "yaar", "ngl", "fr", "lol", "lmao", "omg", "tbh", "fyi",
        "btw", "rly", "jk", "nah", "yeah", "gonna", "wanna", "gotta",
        "ain't", "dunno", "lemme", "kinda", "sorta", "u", "ur", "thru"
    }

    @staticmethod
    def extract_slang_patterns(text: str) -> list[str]:
        """Extract slang patterns from text."""
        words = text.lower().split()
        return [w.strip('.,!?;:') for w in words if w.strip('.,!?;:') in ChatToneLearnerService.SLANG_HINTS]

    @staticmethod
    def extract_emojis(text: str) -> list[str]:
        """Extract emojis from text."""
        emoji_pattern = re.compile(
            "["
            "\U0001F300-\U0001F9FF"
            "\U0001F600-\U0001F64F"
            "\U0001F700-\U0001F77F"
            "\U0001F780-\U0001F7FF"
            "\U0001F800-\U0001F8FF"
            "\U0001F900-\U0001F9FF"
            "\U0001FA00-\U0001FA6F"
            "\U0001FA70-\U0001FAFF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        return emoji_pattern.findall(text)

    @staticmethod
    def calculate_formality_score(text: str, slang_count: int, total_words: int) -> float:
        """Calculate formality score (1.0-5.0, higher = more formal)."""
        formal_markers = ["appreciate", "thank", "please", "kindly", "regards", "sincerely"]
        formal_count = sum(1 for marker in formal_markers if marker in text.lower())

        if total_words == 0:
            return 3.0

        formality = 3.0 + (formal_count * 0.5) - (slang_count * 0.3)
        return max(1.0, min(5.0, formality))

    @staticmethod
    def calculate_avg_message_length(messages: list[ChatMessageLog]) -> float:
        """Calculate average message length in words."""
        if not messages:
            return 0.0
        total_words = sum(len(msg.message_text.split()) for msg in messages)
        return total_words / len(messages)

    @staticmethod
    def calculate_emoji_frequency(messages: list[ChatMessageLog]) -> float:
        """Calculate emoji frequency (0.0-1.0)."""
        if not messages:
            return 0.0
        total_emojis = sum(len(ChatToneLearnerService.extract_emojis(msg.message_text)) for msg in messages)
        total_chars = sum(len(msg.message_text) for msg in messages)
        return min(1.0, total_emojis / max(total_chars, 1) * 100)

    @staticmethod
    def get_common_emojis(messages: list[ChatMessageLog], limit: int = 5) -> list[str]:
        """Get most common emojis used."""
        emoji_counts = {}
        for msg in messages:
            emojis = ChatToneLearnerService.extract_emojis(msg.message_text)
            for emoji in emojis:
                emoji_counts[emoji] = emoji_counts.get(emoji, 0) + 1

        sorted_emojis = sorted(emoji_counts.items(), key=lambda x: x[1], reverse=True)
        return [emoji for emoji, count in sorted_emojis[:limit]]

    @staticmethod
    def get_slang_patterns(messages: list[ChatMessageLog], limit: int = 6) -> list[str]:
        """Get most common slang patterns."""
        slang_counts = {}
        for msg in messages:
            slang = ChatToneLearnerService.extract_slang_patterns(msg.message_text)
            for s in slang:
                slang_counts[s] = slang_counts.get(s, 0) + 1

        sorted_slang = sorted(slang_counts.items(), key=lambda x: x[1], reverse=True)
        return [s for s, count in sorted_slang[:limit]]

    @staticmethod
    def detect_punctuation_style(messages: list[ChatMessageLog]) -> str:
        """Detect punctuation style (expressive, calm, mixed)."""
        if not messages:
            return "unknown"

        total_chars = sum(len(msg.message_text) for msg in messages)
        if total_chars == 0:
            return "unknown"

        exclamation_count = sum(msg.message_text.count("!") for msg in messages)
        question_count = sum(msg.message_text.count("?") for msg in messages)
        punctuation_density = (exclamation_count + question_count) / total_chars

        if punctuation_density > 0.05:
            return "expressive"
        elif punctuation_density < 0.01:
            return "calm"
        else:
            return "balanced"

    @staticmethod
    def detect_caps_usage(messages: list[ChatMessageLog]) -> str:
        """Detect caps usage pattern (minimal, frequent, mixed)."""
        if not messages:
            return "unknown"

        total_letters = sum(sum(1 for c in msg.message_text if c.isalpha()) for msg in messages)
        if total_letters == 0:
            return "unknown"

        all_caps_chars = sum(sum(1 for c in msg.message_text if c.isupper()) for msg in messages)
        caps_ratio = all_caps_chars / total_letters

        if caps_ratio < 0.1:
            return "lowercase"
        elif caps_ratio > 0.3:
            return "frequent"
        else:
            return "mixed"

    @staticmethod
    def detect_language_mix(messages: list[ChatMessageLog]) -> list[str]:
        """Detect language mixing patterns."""
        languages = set()

        for msg in messages:
            text = msg.message_text.lower()

            # Detect English
            if any(ord(c) < 128 for c in text if c.isalpha()):
                languages.add("English")

            # Detect Hindi/Devanagari
            if any(0x0900 <= ord(c) <= 0x097F for c in text):
                languages.add("Hindi")

            # Detect Devanagari combining marks for Hinglish
            if any(0x0900 <= ord(c) <= 0x097F for c in text) and any(ord(c) < 128 for c in text if c.isalpha()):
                languages.add("Hinglish")

        return list(languages) if languages else ["English"]

    @staticmethod
    def get_message_openers(messages: list[ChatMessageLog], limit: int = 5) -> list[str]:
        """Get common message opening patterns."""
        openers = []
        for msg in messages:
            words = msg.message_text.strip().split()
            if words:
                opener = words[0].lower()[:20]
                openers.append(opener)

        opener_counts = {}
        for o in openers:
            opener_counts[o] = opener_counts.get(o, 0) + 1

        sorted_openers = sorted(opener_counts.items(), key=lambda x: x[1], reverse=True)
        return [o for o, count in sorted_openers[:limit]]

    @staticmethod
    def get_message_closers(messages: list[ChatMessageLog], limit: int = 5) -> list[str]:
        """Get common message closing patterns."""
        closers = []
        for msg in messages:
            words = msg.message_text.strip().split()
            if words:
                closer = words[-1].lower()[:20]
                closers.append(closer)

        closer_counts = {}
        for c in closers:
            closer_counts[c] = closer_counts.get(c, 0) + 1

        sorted_closers = sorted(closer_counts.items(), key=lambda x: x[1], reverse=True)
        return [c for c, count in sorted_closers[:limit]]

    @staticmethod
    def learn_chat_specific_tone(
        db: Session,
        chat_config_id: str,
        message_samples: Optional[list[ChatMessageLog]] = None,
    ) -> ChatToneProfile:
        """Extract and store per-chat tone profile.

        Args:
            db: Database session
            chat_config_id: ID of the chat configuration
            message_samples: Optional pre-filtered messages (else fetches from DB)

        Returns:
            Updated or created ChatToneProfile
        """
        if message_samples is None:
            message_samples = ChatToneLearnerService._fetch_user_messages(db, chat_config_id)

        if not message_samples:
            return ChatToneLearnerService._create_empty_profile(db, chat_config_id)

        # Extract patterns
        avg_length = ChatToneLearnerService.calculate_avg_message_length(message_samples)
        emoji_freq = ChatToneLearnerService.calculate_emoji_frequency(message_samples)
        common_emojis = ChatToneLearnerService.get_common_emojis(message_samples)
        slang = ChatToneLearnerService.get_slang_patterns(message_samples)
        punct_style = ChatToneLearnerService.detect_punctuation_style(message_samples)
        caps_usage = ChatToneLearnerService.detect_caps_usage(message_samples)
        languages = ChatToneLearnerService.detect_language_mix(message_samples)
        openers = ChatToneLearnerService.get_message_openers(message_samples)
        closers = ChatToneLearnerService.get_message_closers(message_samples)

        total_words = sum(len(msg.message_text.split()) for msg in message_samples)
        slang_count = len(ChatToneLearnerService.extract_slang_patterns(" ".join(msg.message_text for msg in message_samples)))
        formality = ChatToneLearnerService.calculate_formality_score(" ".join(msg.message_text for msg in message_samples), slang_count, total_words)

        # Get or create profile
        profile = db.query(ChatToneProfile).filter(
            ChatToneProfile.chat_config_id == chat_config_id
        ).first()

        if profile:
            # Update existing profile with new data
            profile.avg_message_length = avg_length
            profile.emoji_frequency = emoji_freq
            profile.common_emojis = common_emojis
            profile.slang_patterns = slang
            profile.punctuation_style = punct_style
            profile.formality_score = formality
            profile.caps_usage = caps_usage
            profile.language_mix = languages
            profile.message_openers = openers
            profile.message_closers = closers
        else:
            # Create new profile
            from app.models import ChatConfig
            chat_config = db.query(ChatConfig).filter(ChatConfig.id == chat_config_id).first()
            if not chat_config:
                raise ValueError(f"Chat config {chat_config_id} not found")

            profile = ChatToneProfile(
                chat_config_id=chat_config_id,
                user_id=chat_config.user_id,
                avg_message_length=avg_length,
                emoji_frequency=emoji_freq,
                common_emojis=common_emojis,
                slang_patterns=slang,
                punctuation_style=punct_style,
                formality_score=formality,
                caps_usage=caps_usage,
                language_mix=languages,
                tone_shifts={},
                message_openers=openers,
                message_closers=closers,
                response_timing={},
            )
            db.add(profile)

        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def compare_global_vs_chat_tone(
        db: Session,
        user_id: str,
        chat_config_id: str,
    ) -> dict:
        """Compare global tone profile with chat-specific tone.

        Args:
            db: Database session
            user_id: ID of the user
            chat_config_id: ID of the chat configuration

        Returns:
            Dictionary with differences and insights
        """
        from app.models import ToneProfile

        global_tone = db.query(ToneProfile).filter(ToneProfile.user_id == user_id).first()
        chat_tone = db.query(ChatToneProfile).filter(ChatToneProfile.chat_config_id == chat_config_id).first()

        if not chat_tone:
            return {"status": "no_chat_tone", "message": "Chat tone profile not trained yet"}

        differences = {
            "avg_message_length": chat_tone.avg_message_length,
            "emoji_frequency": chat_tone.emoji_frequency,
            "formality_score": chat_tone.formality_score,
            "punctuation_style": chat_tone.punctuation_style,
            "caps_usage": chat_tone.caps_usage,
        }

        if global_tone:
            differences["vs_global"] = {
                "length_diff": (chat_tone.avg_message_length or 0) - (global_tone.avg_message_length or 0),
                "emoji_diff": (chat_tone.emoji_frequency or 0) - (global_tone.emoji_frequency or 0),
                "formality_diff": (chat_tone.formality_score or 0) - (global_tone.formality_score or 0),
            }

        return differences

    @staticmethod
    def _fetch_user_messages(db: Session, chat_config_id: str) -> list[ChatMessageLog]:
        """Fetch user's own messages from chat."""
        return db.query(ChatMessageLog).filter(
            ChatMessageLog.chat_config_id == chat_config_id,
            ChatMessageLog.message_role == "user",
        ).order_by(ChatMessageLog.created_at.desc()).limit(500).all()

    @staticmethod
    def _create_empty_profile(db: Session, chat_config_id: str) -> ChatToneProfile:
        """Create an empty tone profile for a chat."""
        from app.models import ChatConfig
        chat_config = db.query(ChatConfig).filter(ChatConfig.id == chat_config_id).first()
        if not chat_config:
            raise ValueError(f"Chat config {chat_config_id} not found")

        profile = ChatToneProfile(
            chat_config_id=chat_config_id,
            user_id=chat_config.user_id,
            tone_shifts={},
            response_timing={},
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
