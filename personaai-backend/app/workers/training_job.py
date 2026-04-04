from app.workers.celery_app import celery_app


@celery_app.task
def run_training_job() -> str:
    return "Training job scaffolded"
