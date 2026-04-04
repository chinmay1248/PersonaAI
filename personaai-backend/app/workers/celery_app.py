from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery("personaai", broker=settings.redis_url, backend=settings.redis_url)

# Eager mode executes tasks synchronously locally without needing a Redis instance.
celery_app.conf.update(
    task_always_eager=True,
    task_eager_propagates=True,
)
