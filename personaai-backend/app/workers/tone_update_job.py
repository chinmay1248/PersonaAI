from app.workers.celery_app import celery_app


@celery_app.task
def refresh_tone_profiles() -> str:
    return "Tone refresh job scaffolded"
