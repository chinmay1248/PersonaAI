from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ChatMessageLog(Base):
    __tablename__ = "chat_message_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    chat_config_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_configs.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    message_role: Mapped[str] = mapped_column(String(20), nullable=False)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    detected_mood: Mapped[str | None] = mapped_column(String(50), nullable=True)
    language_detected: Mapped[str | None] = mapped_column(String(20), nullable=True)
    thread_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("conversation_threads.id", ondelete="SET NULL"), index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    chat_config = relationship("ChatConfig", back_populates="message_logs")
    user = relationship("User", back_populates="chat_message_logs")
    thread = relationship("ConversationThread", back_populates="messages")

    __table_args__ = (
        Index("idx_chat_config_created", "chat_config_id", "created_at"),
        Index("idx_user_created", "user_id", "created_at"),
    )
