from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.feedback import ReplyFeedbackRequest, ReplyFeedbackResponse
from app.services.feedback_processor import FeedbackProcessorService
from app.utils.validators import VALID_FEEDBACK_RATINGS

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/reply", response_model=ReplyFeedbackResponse)
def submit_feedback(
    payload: ReplyFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReplyFeedbackResponse:
    if payload.rating not in VALID_FEEDBACK_RATINGS:
        raise HTTPException(status_code=400, detail="Unsupported feedback rating")

    try:
        FeedbackProcessorService.record_feedback(
            db=db,
            user_id=current_user.id,
            reply_suggestion_id=payload.reply_suggestion_id,
            rating=payload.rating,
            reason=payload.reason,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return ReplyFeedbackResponse(
        status="recorded",
        message="AI will improve based on your feedback",
    )
