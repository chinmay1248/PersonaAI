from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models import ChatConfig, User
from app.services.chat_history_service import ChatHistoryService
from app.services.chat_tone_learner import ChatToneLearnerService

router = APIRouter(prefix="/chats", tags=["chat_history"])


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    text: str
    mood: Optional[str] = None
    language: Optional[str] = None
    timestamp: str


class ChatHistoryResponse(BaseModel):
    chat_id: str
    chat_label: str
    messages: list[MessageResponse]
    total_count: int


class ChatToneProfileResponse(BaseModel):
    chat_config_id: str
    avg_message_length: Optional[float] = None
    emoji_frequency: Optional[float] = None
    common_emojis: list[str]
    slang_patterns: list[str]
    punctuation_style: Optional[str] = None
    formality_score: Optional[float] = None
    caps_usage: Optional[str] = None
    language_mix: list[str]
    message_openers: list[str]
    message_closers: list[str]


@router.get("/{chat_config_id}/history", response_model=ChatHistoryResponse)
def get_chat_history(
    chat_config_id: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    mood_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve chat message history."""
    # Verify ownership
    chat_config = db.query(ChatConfig).filter(
        ChatConfig.id == chat_config_id,
        ChatConfig.user_id == current_user.id,
    ).first()

    if not chat_config:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages = ChatHistoryService.get_chat_history(db, chat_config_id, limit=limit, offset=offset)

    if mood_filter:
        messages = [m for m in messages if m.detected_mood == mood_filter]

    return ChatHistoryResponse(
        chat_id=chat_config_id,
        chat_label=chat_config.chat_label,
        messages=[
            MessageResponse(
                id=m.id,
                role=m.message_role,
                text=m.message_text,
                mood=m.detected_mood,
                language=m.language_detected,
                timestamp=m.created_at.isoformat(),
            )
            for m in messages
        ],
        total_count=ChatHistoryService.get_message_count(db, chat_config_id),
    )


@router.get("/{chat_config_id}/history/recent", response_model=ChatHistoryResponse)
def get_recent_messages(
    chat_config_id: str,
    minutes: int = Query(1440, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get messages from the last N minutes."""
    chat_config = db.query(ChatConfig).filter(
        ChatConfig.id == chat_config_id,
        ChatConfig.user_id == current_user.id,
    ).first()

    if not chat_config:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages = ChatHistoryService.get_recent_messages(db, chat_config_id, minutes=minutes)

    return ChatHistoryResponse(
        chat_id=chat_config_id,
        chat_label=chat_config.chat_label,
        messages=[
            MessageResponse(
                id=m.id,
                role=m.message_role,
                text=m.message_text,
                mood=m.detected_mood,
                language=m.language_detected,
                timestamp=m.created_at.isoformat(),
            )
            for m in messages
        ],
        total_count=len(messages),
    )


@router.get("/{chat_config_id}/tone-profile", response_model=ChatToneProfileResponse)
def get_chat_tone_profile(
    chat_config_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get per-chat tone profile."""
    chat_config = db.query(ChatConfig).filter(
        ChatConfig.id == chat_config_id,
        ChatConfig.user_id == current_user.id,
    ).first()

    if not chat_config:
        raise HTTPException(status_code=404, detail="Chat not found")

    from app.models import ChatToneProfile
    tone_profile = db.query(ChatToneProfile).filter(
        ChatToneProfile.chat_config_id == chat_config_id
    ).first()

    if not tone_profile:
        raise HTTPException(status_code=404, detail="Tone profile not trained yet")

    return ChatToneProfileResponse(
        chat_config_id=tone_profile.chat_config_id,
        avg_message_length=tone_profile.avg_message_length,
        emoji_frequency=tone_profile.emoji_frequency,
        common_emojis=tone_profile.common_emojis or [],
        slang_patterns=tone_profile.slang_patterns or [],
        punctuation_style=tone_profile.punctuation_style,
        formality_score=tone_profile.formality_score,
        caps_usage=tone_profile.caps_usage,
        language_mix=tone_profile.language_mix or [],
        message_openers=tone_profile.message_openers or [],
        message_closers=tone_profile.message_closers or [],
    )


@router.post("/{chat_config_id}/retrain-tone")
def retrain_chat_tone(
    chat_config_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Force recompute chat-specific tone profile."""
    chat_config = db.query(ChatConfig).filter(
        ChatConfig.id == chat_config_id,
        ChatConfig.user_id == current_user.id,
    ).first()

    if not chat_config:
        raise HTTPException(status_code=404, detail="Chat not found")

    tone_profile = ChatToneLearnerService.learn_chat_specific_tone(db, chat_config_id)

    return {
        "status": "trained",
        "chat_config_id": chat_config_id,
        "avg_message_length": tone_profile.avg_message_length,
        "emoji_frequency": tone_profile.emoji_frequency,
        "formality_score": tone_profile.formality_score,
    }


@router.get("/{chat_config_id}/export")
def export_chat_history(
    chat_config_id: str,
    include_encrypted: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export full chat history as JSON."""
    chat_config = db.query(ChatConfig).filter(
        ChatConfig.id == chat_config_id,
        ChatConfig.user_id == current_user.id,
    ).first()

    if not chat_config:
        raise HTTPException(status_code=404, detail="Chat not found")

    export_data = ChatHistoryService.export_chat_history(db, chat_config_id, include_encrypted)
    return export_data
