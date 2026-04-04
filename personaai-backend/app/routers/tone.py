from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.tone_profile import ToneProfile
from app.models.user import User
from app.schemas.tone import ToneProfileResponse, TrainToneRequest
from app.services.tone_learner import ToneLearnerService

router = APIRouter(prefix="/tone", tags=["tone"])


def _to_response(profile: ToneProfile) -> ToneProfileResponse:
    return ToneProfileResponse(
        profile_id=profile.id,
        formality_score=profile.formality_score or 0.0,
        avg_message_length=profile.avg_message_length or 0.0,
        emoji_frequency=profile.emoji_frequency or 0.0,
        common_emojis=profile.common_emojis,
        slang_patterns=profile.slang_patterns,
        detected_language_mix=profile.language_mix,
        accuracy_score=profile.accuracy_score,
        status="trained",
    )


@router.post("/train", response_model=ToneProfileResponse)
def train_tone(
    payload: TrainToneRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ToneProfileResponse:
    profile = ToneLearnerService.train(db, current_user.id, payload.samples)
    return _to_response(profile)


@router.get("/profile", response_model=ToneProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ToneProfileResponse:
    profile = db.query(ToneProfile).filter(ToneProfile.user_id == current_user.id).one_or_none()
    if not profile:
        profile = ToneLearnerService.train(
            db,
            current_user.id,
            ["hey there", "sounds good", "let me get back to you soon"],
        )
    return _to_response(profile)
