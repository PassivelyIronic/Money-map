from celery import Celery

from app.config import settings

celery_app = Celery(
    "money_map",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Warsaw",
    enable_utc=True,
    # importy CSV + kategoryzacja Ollama moga trwac dluzej niz domyslny limit
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)
