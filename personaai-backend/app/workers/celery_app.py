from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery("personaai", broker=settings.redis_url, backend=settings.redis_url)

# Configuration for task execution
# In production: task_always_eager=False (use actual Redis broker)
# In development: task_always_eager=True (execute synchronously locally)
is_production = settings.app_env == "production"

celery_app.conf.update(
    task_always_eager=not is_production,  # Sync mode for dev, async for prod
    task_eager_propagates=not is_production,
    # Celery Beat scheduler (for periodic tasks)
    beat_schedule={
        "train-every-15-min": {
            "task": "app.workers.training_job.run_training_job",
            "schedule": 60.0 * 15,  # Every 15 minutes
            "options": {"queue": "default"},
        },
        "refresh-tone-profiles-hourly": {
            "task": "app.workers.tone_update_job.refresh_tone_profiles",
            "schedule": 60.0 * 60,  # Every 1 hour
            "options": {"queue": "default"},
        },
    },
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,  # Acknowledge task after execution
    task_reject_on_worker_lost=True,  # Reject task if worker dies
    # Worker settings
    worker_prefetch_multiplier=1,  # Fetch one task at a time
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
)
