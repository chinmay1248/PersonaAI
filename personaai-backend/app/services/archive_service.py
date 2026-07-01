from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.chat_message_log import ChatMessageLog

class ArchiveService:
    @staticmethod
    def delete_old_messages(db: Session, days: int = 90) -> int:
        """Deletes chat message logs older than the specified number of days."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        deleted_count = db.query(ChatMessageLog).filter(ChatMessageLog.created_at < cutoff_date).delete()
        db.commit()
        return deleted_count
