"""
Celery application configuration.
"""
from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "voicecanvas",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configure Celery
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    timezone="UTC",
    enable_utc=True,
)
