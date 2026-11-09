from celery import Celery

from app.config import settings

celery_app = Celery(
    "jobflow",
    broker=settings.broker_url,
    backend=settings.result_backend,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    result_expires=settings.result_expires_seconds,
    broker_connection_retry_on_startup=True,
    timezone="UTC",
)
