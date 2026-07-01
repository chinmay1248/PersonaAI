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
    def get_positive_reply_patterns(db: Session, user_id: str, limit: int = 5) -> list[str]:
        """Fetch texts of replies recently rated as 'liked'."""
        from app.services.encryption import EncryptionService
        logs = db.query(FeedbackLog).filter(
            FeedbackLog.user_id == user_id,
            FeedbackLog.rating == "liked"
        ).order_by(FeedbackLog.created_at.desc()).limit(limit).all()

        patterns = []
        for log in logs:
            suggestion = db.get(ReplySuggestion, log.reply_suggestion_id)
            if suggestion:
                patterns.append(EncryptionService.decrypt(suggestion.reply_text))
        return patterns

    @staticmethod
    def get_negative_reply_patterns(db: Session, user_id: str, limit: int = 5) -> list[str]:
        """Fetch texts of replies recently rated as 'disliked'."""
        from app.services.encryption import EncryptionService
        logs = db.query(FeedbackLog).filter(
            FeedbackLog.user_id == user_id,
            FeedbackLog.rating == "disliked"
        ).order_by(FeedbackLog.created_at.desc()).limit(limit).all()

        patterns = []
        for log in logs:
            suggestion = db.get(ReplySuggestion, log.reply_suggestion_id)
            if suggestion:
                patterns.append(EncryptionService.decrypt(suggestion.reply_text))
        return patterns
