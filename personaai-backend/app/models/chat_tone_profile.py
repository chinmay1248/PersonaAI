from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ChatToneProfile(Base):
    __tablename__ = "chat_tone_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    chat_config_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_configs.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    avg_message_length: Mapped[float | None] = mapped_column(Float, nullable=True)
    emoji_frequency: Mapped[float | None] = mapped_column(Float, nullable=True)
    common_emojis: Mapped[list[str]] = mapped_column(JSON, default=list)
    slang_patterns: Mapped[list[str]] = mapped_column(JSON, default=list)
    punctuation_style: Mapped[str | None] = mapped_column(String(50), nullable=True)
    formality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    caps_usage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    language_mix: Mapped[list[str]] = mapped_column(JSON, default=list)
    tone_shifts: Mapped[dict] = mapped_column(JSON, default=dict)
    message_openers: Mapped[list[str]] = mapped_column(JSON, default=list)
    message_closers: Mapped[list[str]] = mapped_column(JSON, default=list)
    response_timing: Mapped[dict] = mapped_column(JSON, default=dict)
    last_trained_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    chat_config = relationship("ChatConfig", back_populates="tone_profiles")
    user = relationship("User", back_populates="chat_tone_profiles")
