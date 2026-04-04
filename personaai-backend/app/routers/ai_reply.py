from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.ai import GenerateReplyRequest, GenerateReplyResponse, ReplySuggestionItem
from app.services.ai_engine import AIEngineService
from app.services.encryption import EncryptionService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/generate-reply", response_model=GenerateReplyResponse)
def generate_reply(
    payload: GenerateReplyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GenerateReplyResponse:
    try:
        conversation, suggestions, detected_mood = AIEngineService.generate_replies(db, current_user.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return GenerateReplyResponse(
        conversation_id=conversation.id,
        detected_mood=detected_mood,
        suggestions=[
            ReplySuggestionItem(id=item.id, rank=item.rank or 0, text=EncryptionService.decrypt(item.reply_text))
            for item in suggestions
        ],
    )
