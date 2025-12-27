"""Tasks module."""
from app.tasks.celery_app import celery_app
from app.tasks.parse_tasks import parse_local, parse_upstage_submit, parse_upstage_poll, parse_upstage_download
from app.tasks.index_tasks import index_document, reindex_document

__all__ = [
    "celery_app",
    "parse_local",
    "parse_upstage_submit",
    "parse_upstage_poll",
    "parse_upstage_download",
    "index_document",
    "reindex_document",
]
