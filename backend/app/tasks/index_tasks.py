"""Celery tasks for indexing."""
import logging
from datetime import datetime
from app.tasks.celery_app import celery_app
from app.services.minio_service import minio_service
from app.services.chunking import text_chunker
from app.services.elasticsearch_service import elasticsearch_service
from app.database import SessionLocal
from app.models import DocumentVersion

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.index_tasks.index_document")
def index_document(doc_id: str, version_id: str):
    """
    Index parsed document to Elasticsearch.

    Args:
        doc_id: Document ID
        version_id: Version ID
    """
    db = SessionLocal()
    try:
        # Get document version
        doc_version = (
            db.query(DocumentVersion)
            .filter_by(doc_id=doc_id, version_id=version_id)
            .first()
        )

        if not doc_version:
            logger.error(f"Document version not found: {doc_id}/{version_id}")
            return

        if doc_version.status != "parsed":
            logger.warning(f"Document not in parsed state: {doc_version.status}")
            return

        # Update status
        doc_version.status = "indexing"
        db.commit()

        # Download normalized JSON
        logger.info(f"Downloading normalized JSON from {doc_version.result_json_uri}")
        normalized_json = minio_service.download_json(doc_version.result_json_uri)

        # Chunk document
        logger.info(f"Chunking document {doc_id}/{version_id}")
        chunks = text_chunker.chunk_normalized_json(normalized_json)

        if not chunks:
            logger.warning(f"No chunks created for {doc_id}/{version_id}")
            doc_version.status = "indexed"
            db.commit()
            return

        # Add timestamp to chunks
        for chunk in chunks:
            chunk["created_at"] = datetime.utcnow().isoformat()

        # Index to Elasticsearch
        logger.info(f"Indexing {len(chunks)} chunks to Elasticsearch")
        elasticsearch_service.index_chunks(chunks)

        # Update status
        doc_version.status = "indexed"
        doc_version.updated_at = datetime.utcnow()
        db.commit()

        logger.info(f"Successfully indexed {doc_id}/{version_id}")

    except Exception as e:
        logger.error(f"Error indexing document: {e}")
        doc_version.status = "failed"
        doc_version.last_error = str(e)
        db.commit()
        raise

    finally:
        db.close()


@celery_app.task(name="app.tasks.index_tasks.reindex_document")
def reindex_document(doc_id: str, version_id: str):
    """
    Re-index document (delete old chunks and index new ones).

    Args:
        doc_id: Document ID
        version_id: Version ID
    """
    db = SessionLocal()
    try:
        # Delete existing chunks
        logger.info(f"Deleting existing chunks for {doc_id}/{version_id}")
        elasticsearch_service.delete_by_doc_version(doc_id, version_id)

        # Re-index
        index_document(doc_id, version_id)

    except Exception as e:
        logger.error(f"Error re-indexing document: {e}")
        raise

    finally:
        db.close()
