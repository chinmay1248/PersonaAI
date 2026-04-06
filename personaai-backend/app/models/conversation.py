from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    chat_config_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_configs.id"), index=True)
    incoming_msg: Mapped[str] = mapped_column(Text, nullable=False)
    detected_mood: Mapped[str | None] = mapped_column(String(50), nullable=True)
    context_window: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="conversations")
    chat_config = relationship("ChatConfig", back_populates="conversations")
    reply_suggestions = relationship("ReplySuggestion", back_populates="conversation", cascade="all, delete-orphan")
