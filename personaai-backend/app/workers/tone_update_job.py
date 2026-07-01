from app.workers.celery_app import celery_app


@celery_app.task
def refresh_tone_profiles() -> str:
    """
    Periodically recalculate tone profiles for active users.
    Pulls all training samples marked as used_in_training and
    rebuilds the tone analysis to keep accuracy scores current.
    """
    from app.database import SessionLocal
    from app.models.tone_profile import ToneProfile
    from app.models.training_sample import TrainingSample
    from app.services.tone_learner import ToneLearnerService

    db = SessionLocal()
    try:
        # Find all users who have a tone profile
        profiles = db.query(ToneProfile).all()

        if not profiles:
            return "No tone profiles to refresh"

        refreshed_count = 0
        for profile in profiles:
            # Pull all trained samples for this user
            samples = (
                db.query(TrainingSample)
                .filter(
                    TrainingSample.user_id == profile.user_id,
                    TrainingSample.used_in_training == True,  # noqa: E712
                )
                .order_by(TrainingSample.created_at.desc())
                .limit(100)
                .all()
            )

            if not samples:
                continue

            sample_texts = [s.sample_text for s in samples]
            ToneLearnerService.train(db, profile.user_id, sample_texts)
            refreshed_count += 1

        return f"Refreshed {refreshed_count} tone profiles"
    except Exception as exc:
        db.rollback()
        return f"Tone refresh job failed: {exc}"
    finally:
        db.close()


@celery_app.task
def cleanup_old_messages_job() -> str:
    """
    Periodically clean up chat messages older than 90 days
    to save space and protect privacy.
    """
    from app.database import SessionLocal
    from app.models.chat_config import ChatConfig
    from app.services.chat_history_service import ChatHistoryService

    db = SessionLocal()
    try:
        chats = db.query(ChatConfig).all()
        if not chats:
            return "No chats to clean up"

        total_deleted = 0
        for chat in chats:
            deleted = ChatHistoryService.delete_old_messages(db, chat.id, days_to_keep=90)
            total_deleted += deleted

        return f"Deleted {total_deleted} old messages across {len(chats)} chats"
    except Exception as exc:
        db.rollback()
        return f"Message cleanup job failed: {exc}"
    finally:
        db.close()
