"""Celery application configuration."""
from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "pdf_rag_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # 55 minutes soft limit
)

# Task routing
celery_app.conf.task_routes = {
    "app.tasks.parse_tasks.*": {"queue": "parse_queue"},
    "app.tasks.index_tasks.*": {"queue": "index_queue"},
}

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
