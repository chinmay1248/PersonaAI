from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.tone_profile import ToneProfile
from app.models.user import User
from app.schemas.tone import ToneProfileResponse, TrainToneRequest, TrainFromMessagesRequest, TrainingStatsResponse
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


@router.post("/train-from-messages", response_model=ToneProfileResponse)
def train_from_messages(
    payload: TrainFromMessagesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ToneProfileResponse:
    """
    Continuously train tone profile from real chat messages (WhatsApp, Telegram, etc).
    This merges new message patterns with existing tone profile.
    """
    profile = ToneLearnerService.train_from_messages(db, current_user.id, payload.messages, payload.source)
    return _to_response(profile)


@router.get("/training-stats", response_model=TrainingStatsResponse)
def get_training_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrainingStatsResponse:
    """Get statistics about how much the AI has learned about your communication style."""
    profile = db.query(ToneProfile).filter(ToneProfile.user_id == current_user.id).one_or_none()

    if not profile:
        return TrainingStatsResponse(
            total_samples_trained=0,
            whatsapp_samples=0,
            manual_samples=0,
            last_training_time=None,
            accuracy_score=0.0,
            most_common_slang=[],
        )

    # Count training samples by source
    from app.models.training_sample import TrainingSample

    total_samples = db.query(TrainingSample).filter(
        TrainingSample.user_id == current_user.id, TrainingSample.used_in_training == True
    ).count()

    whatsapp_samples = db.query(TrainingSample).filter(
        TrainingSample.user_id == current_user.id,
        TrainingSample.source == "whatsapp",
        TrainingSample.used_in_training == True,
    ).count()

    manual_samples = db.query(TrainingSample).filter(
        TrainingSample.user_id == current_user.id,
        TrainingSample.source == "manual",
        TrainingSample.used_in_training == True,
    ).count()

    return TrainingStatsResponse(
        total_samples_trained=total_samples,
        whatsapp_samples=whatsapp_samples,
        manual_samples=manual_samples,
        last_training_time=profile.last_trained_at.isoformat() if profile.last_trained_at else None,
        accuracy_score=profile.accuracy_score,
        most_common_slang=profile.slang_patterns[:10],
    )


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


@router.post("/enable-auto-training")
def enable_auto_training(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Enable automatic training from WhatsApp messages."""
    current_user.auto_training_enabled = True
    db.commit()
    return {"message": "Auto-training enabled", "auto_training_enabled": True}


@router.post("/disable-auto-training")
def disable_auto_training(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Disable automatic training from WhatsApp messages."""
    current_user.auto_training_enabled = False
    db.commit()
    return {"message": "Auto-training disabled", "auto_training_enabled": False}
