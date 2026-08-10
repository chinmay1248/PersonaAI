from sqlalchemy.orm import Session

from app.models.feedback_log import FeedbackLog
from app.models.reply_suggestion import ReplySuggestion


class FeedbackProcessorService:
    @staticmethod
    def record_feedback(db: Session, user_id: str, reply_suggestion_id: str, rating: str, reason: str | None) -> None:
        suggestion = db.get(ReplySuggestion, reply_suggestion_id)
        if not suggestion:
            raise ValueError("Reply suggestion not found")

        suggestion.feedback = rating
        suggestion.feedback_reason = reason
        db.add(
            FeedbackLog(
                user_id=user_id,
                reply_suggestion_id=reply_suggestion_id,
                rating=rating,
                reason=reason,
            )
        )
        db.commit()

    @staticmethod
    def get_positive_reply_patterns(
        db: Session,
        user_id: str,
        limit: int = 5,
        chat_config_id: str | None = None,
    ) -> list[str]:
        """Fetch texts of replies recently rated as 'liked'."""
        return FeedbackProcessorService._get_rated_reply_texts(
            db, user_id, "liked", limit, chat_config_id
        )

    @staticmethod
    def get_negative_reply_patterns(
        db: Session,
        user_id: str,
        limit: int = 5,
        chat_config_id: str | None = None,
    ) -> list[str]:
        """Fetch texts of replies recently rated as 'disliked'."""
        return FeedbackProcessorService._get_rated_reply_texts(
            db, user_id, "disliked", limit, chat_config_id
        )

    @staticmethod
    def _get_rated_reply_texts(
        db: Session,
        user_id: str,
        rating: str,
        limit: int,
        chat_config_id: str | None,
    ) -> list[str]:
        from app.models.conversation import Conversation
        from app.services.encryption import EncryptionService

        query = db.query(FeedbackLog).filter(
            FeedbackLog.user_id == user_id,
            FeedbackLog.rating == rating,
        )

        # Rated replies are shown to the model as style examples, and a small model
        # will happily lift their wording. Scoping them to the chat keeps another
        # conversation's names and plans out of these suggestions.
        if chat_config_id:
            query = query.join(
                ReplySuggestion, ReplySuggestion.id == FeedbackLog.reply_suggestion_id
            ).join(
                Conversation, Conversation.id == ReplySuggestion.conversation_id
            ).filter(Conversation.chat_config_id == chat_config_id)

        logs = query.order_by(FeedbackLog.created_at.desc()).limit(limit).all()

        patterns = []
        for log in logs:
            suggestion = db.get(ReplySuggestion, log.reply_suggestion_id)
            if suggestion:
                patterns.append(EncryptionService.decrypt(suggestion.reply_text))
        return patterns
