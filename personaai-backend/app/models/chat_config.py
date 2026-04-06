from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ChatConfig(Base):
    __tablename__ = "chat_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    chat_label: Mapped[str] = mapped_column(String(100), nullable=False)
    chat_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    personality_mode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    auto_reply_mode: Mapped[str] = mapped_column(String(20), default="OFF")
    ai_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="chat_configs")
    conversations = relationship("Conversation", back_populates="chat_config")
