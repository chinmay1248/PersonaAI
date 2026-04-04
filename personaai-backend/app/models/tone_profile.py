from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ToneProfile(Base):
    __tablename__ = "tone_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    formality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_message_length: Mapped[float | None] = mapped_column(Float, nullable=True)
    emoji_frequency: Mapped[float | None] = mapped_column(Float, nullable=True)
    common_emojis: Mapped[list[str]] = mapped_column(JSON, default=list)
    slang_patterns: Mapped[list[str]] = mapped_column(JSON, default=list)
    punctuation_style: Mapped[str | None] = mapped_column(String(50), nullable=True)
    caps_usage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    language_mix: Mapped[list[str]] = mapped_column(JSON, default=list)
    vector_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    accuracy_score: Mapped[float] = mapped_column(Float, default=0.0)
    last_trained_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tone_profiles")
