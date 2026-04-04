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
