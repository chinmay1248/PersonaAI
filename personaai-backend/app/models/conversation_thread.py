from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ConversationThread(Base):
    __tablename__ = "conversation_threads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    chat_config_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_configs.id", ondelete="CASCADE"), index=True)
    topic_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    chat_config = relationship("ChatConfig")
    messages = relationship("ChatMessageLog", back_populates="thread")

    __table_args__ = (
        Index("idx_thread_chat_config", "chat_config_id"),
    )
