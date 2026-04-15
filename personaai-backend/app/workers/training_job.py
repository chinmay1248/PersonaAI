from app.workers.celery_app import celery_app


@celery_app.task
def run_training_job() -> str:
    """
    Process untrained samples and feed them into the tone learner.
    This job is meant to run periodically (e.g. every 15 minutes)
    to pick up samples that were stored but not yet used in training.
    """
    from app.database import SessionLocal
    from app.models.training_sample import TrainingSample
    from app.models.user import User
    from app.services.tone_learner import ToneLearnerService

    db = SessionLocal()
    try:
        # Find all users who have untrained samples
        untrained = (
            db.query(TrainingSample)
            .filter(TrainingSample.used_in_training == False)  # noqa: E712
            .all()
        )

        if not untrained:
            return "No untrained samples found"

        # Group by user_id
        user_samples: dict[str, list[str]] = {}
        for sample in untrained:
            user_samples.setdefault(sample.user_id, []).append(sample.sample_text)

        trained_count = 0
        for user_id, samples in user_samples.items():
            user = db.get(User, user_id)
            if not user:
                continue

            source = untrained[0].source or "manual"
            ToneLearnerService.train_from_messages(db, user_id, samples, source)
            trained_count += len(samples)

        return f"Trained {trained_count} samples across {len(user_samples)} users"
    except Exception as exc:
        db.rollback()
        return f"Training job failed: {exc}"
    finally:
        db.close()
