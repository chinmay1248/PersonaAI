from fastapi import APIRouter, Depends

from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.ai import SummarizeRequest, SummarizeResponse
from app.services.summarizer import SummarizerService

router = APIRouter(prefix="/ai", tags=["summarizer"])


@router.post("/summarize", response_model=SummarizeResponse)
def summarize_messages(
    payload: SummarizeRequest,
    current_user: User = Depends(get_current_user),
) -> SummarizeResponse:
    summary, action_items = SummarizerService.summarize(payload.messages)
    return SummarizeResponse(summary=summary, action_items=action_items)
