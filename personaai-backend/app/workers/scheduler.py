"""
Celery Beat scheduler configuration for periodic tasks.

Schedules:
- run_training_job: Every 15 minutes (process untrained samples)
- refresh_tone_profiles: Every 1 hour (refresh tone analysis)
"""

from celery.schedules import crontab
from app.workers.celery_app import celery_app

# Configure Celery Beat schedule
celery_app.conf.beat_schedule = {
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
}

# Configure Celery app settings for production
celery_app.conf.update(
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
