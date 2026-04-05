from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.chat_config import ChatConfig
from app.models.user import User
from app.schemas.chat import ChatConfigCreateRequest, ChatConfigResponse, ChatConfigUpdateRequest
from app.utils.validators import VALID_AUTO_REPLY_MODES, VALID_PERSONALITY_MODES

router = APIRouter(prefix="/chats", tags=["chat-configs"])


@router.get("/config", response_model=list[ChatConfigResponse])
def get_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatConfigResponse]:
    """Get all chat configurations for the current user."""
    configs = db.query(ChatConfig).filter(ChatConfig.user_id == current_user.id).all()
    return [
        ChatConfigResponse(
            id=config.id,
            chat_label=config.chat_label,
            chat_type=config.chat_type,
            personality_mode=config.personality_mode,
            auto_reply_mode=config.auto_reply_mode,
            ai_enabled=config.ai_enabled,
            is_private=config.is_private,
        )
        for config in configs
    ]


@router.post("/config", response_model=ChatConfigResponse, status_code=status.HTTP_201_CREATED)
def create_config(
    payload: ChatConfigCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatConfigResponse:
    if payload.personality_mode and payload.personality_mode not in VALID_PERSONALITY_MODES:
        raise HTTPException(status_code=400, detail="Unsupported personality mode")
    if payload.auto_reply_mode not in VALID_AUTO_REPLY_MODES:
        raise HTTPException(status_code=400, detail="Unsupported auto reply mode")

    config = ChatConfig(user_id=current_user.id, **payload.model_dump())
    db.add(config)
    db.commit()
    db.refresh(config)

    return ChatConfigResponse(
        id=config.id,
        chat_label=config.chat_label,
        chat_type=config.chat_type,
        personality_mode=config.personality_mode,
        auto_reply_mode=config.auto_reply_mode,
        ai_enabled=config.ai_enabled,
        is_private=config.is_private,
    )


@router.patch("/config/{config_id}", response_model=ChatConfigResponse)
def update_config(
    config_id: str,
    payload: ChatConfigUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatConfigResponse:
    config = db.get(ChatConfig, config_id)
    if not config or config.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Chat configuration not found")

    updates = payload.model_dump(exclude_unset=True)
    if "personality_mode" in updates and updates["personality_mode"] not in VALID_PERSONALITY_MODES:
        raise HTTPException(status_code=400, detail="Unsupported personality mode")
    if "auto_reply_mode" in updates and updates["auto_reply_mode"] not in VALID_AUTO_REPLY_MODES:
        raise HTTPException(status_code=400, detail="Unsupported auto reply mode")

    for key, value in updates.items():
        setattr(config, key, value)

    db.commit()
    db.refresh(config)

    return ChatConfigResponse(
        id=config.id,
        chat_label=config.chat_label,
        chat_type=config.chat_type,
        personality_mode=config.personality_mode,
        auto_reply_mode=config.auto_reply_mode,
        ai_enabled=config.ai_enabled,
        is_private=config.is_private,
    )
