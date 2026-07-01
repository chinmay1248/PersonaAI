"""
Celery Beat scheduler configuration for periodic tasks.

Schedules:
- run_training_job: Every 15 minutes (process untrained samples)
- refresh_tone_profiles: Every 1 hour (refresh tone analysis)
- cleanup_old_messages_job: Once a day (cleanup)
"""

from celery.schedules import crontab
from app.workers.celery_app import celery_app
from app.workers.training_job import run_training_job
from app.workers.tone_update_job import refresh_tone_profiles, cleanup_old_messages_job


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs) -> None:
    # Run the incremental training job every 15 minutes
    sender.add_periodic_task(
        crontab(minute="*/15"),
        run_training_job.s(),
        name="incremental-training-every-15m",
    )

    # Run the full tone refresh job once a day at 2:00 AM
    sender.add_periodic_task(
        crontab(hour=2, minute=0),
        refresh_tone_profiles.s(),
        name="daily-tone-refresh",
    )

    # Run message cleanup once a day at 3:00 AM
    sender.add_periodic_task(
        crontab(hour=3, minute=0),
        cleanup_old_messages_job.s(),
        name="daily-message-cleanup",
    )

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
