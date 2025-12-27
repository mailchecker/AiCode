"""Celery tasks for PDF parsing."""
import time
import logging
from datetime import datetime
from app.tasks.celery_app import celery_app
from app.services.minio_service import minio_service
from app.services.pdf_parser.local_parser import LocalPDFParser
from app.services.pdf_parser.upstage_parser import upstage_parser
from app.database import SessionLocal
from app.models import DocumentVersion
from app.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.parse_tasks.parse_local")
def parse_local(doc_id: str, version_id: str):
    """
    Parse PDF using local parser.

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

        # Update status
        doc_version.status = "parsing"
        doc_version.attempt_count += 1
        db.commit()

        # Download PDF from MinIO
        logger.info(f"Downloading PDF from {doc_version.pdf_uri}")
        pdf_bytes = minio_service.download_pdf(doc_version.pdf_uri)

        # Parse locally
        logger.info(f"Parsing PDF locally for {doc_id}/{version_id}")
        parser = LocalPDFParser()
        normalized_json = parser.parse(pdf_bytes, doc_id, version_id)

        # Upload result to MinIO
        logger.info(f"Uploading normalized JSON for {doc_id}/{version_id}")
        json_uri = minio_service.upload_json(doc_id, version_id, normalized_json)

        # Update status
        doc_version.status = "parsed"
        doc_version.result_json_uri = json_uri
        doc_version.updated_at = datetime.utcnow()
        db.commit()

        logger.info(f"Successfully parsed {doc_id}/{version_id} locally")

        # Trigger indexing
        from app.tasks.index_tasks import index_document
        index_document.delay(doc_id, version_id)

    except Exception as e:
        logger.error(f"Error in local parsing: {e}")
        doc_version.status = "failed"
        doc_version.last_error = str(e)
        db.commit()
        raise

    finally:
        db.close()


@celery_app.task(name="app.tasks.parse_tasks.parse_upstage_submit")
def parse_upstage_submit(doc_id: str, version_id: str):
    """
    Submit PDF to Upstage API for parsing.

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

        # Update status
        doc_version.status = "parsing"
        doc_version.attempt_count += 1
        db.commit()

        # Download PDF from MinIO
        logger.info(f"Downloading PDF from {doc_version.pdf_uri}")
        pdf_bytes = minio_service.download_pdf(doc_version.pdf_uri)

        # Submit to Upstage
        logger.info(f"Submitting PDF to Upstage for {doc_id}/{version_id}")
        request_id = upstage_parser.submit_parse_request(pdf_bytes, f"{doc_id}.pdf")

        # Save request_id
        doc_version.parse_request_id = request_id
        doc_version.updated_at = datetime.utcnow()
        db.commit()

        logger.info(f"Upstage request_id: {request_id}")

        # Start polling task
        parse_upstage_poll.delay(doc_id, version_id, request_id)

    except Exception as e:
        logger.error(f"Error submitting to Upstage: {e}")
        doc_version.status = "failed"
        doc_version.last_error = str(e)
        db.commit()
        raise

    finally:
        db.close()


@celery_app.task(name="app.tasks.parse_tasks.parse_upstage_poll")
def parse_upstage_poll(doc_id: str, version_id: str, request_id: str, attempt: int = 0):
    """
    Poll Upstage API for parsing status.

    Args:
        doc_id: Document ID
        version_id: Version ID
        request_id: Upstage request ID
        attempt: Current polling attempt
    """
    db = SessionLocal()
    try:
        # Check max attempts
        if attempt >= settings.upstage_poll_max_attempts:
            logger.error(f"Max polling attempts reached for {doc_id}/{version_id}")
            doc_version = (
                db.query(DocumentVersion)
                .filter_by(doc_id=doc_id, version_id=version_id)
                .first()
            )
            doc_version.status = "failed"
            doc_version.last_error = "Upstage polling timeout"
            db.commit()
            return

        # Check status
        logger.info(f"Polling Upstage (attempt {attempt}) for {doc_id}/{version_id}")
        status_response = upstage_parser.check_status(request_id)

        status = status_response.get("status")

        if status == "completed":
            logger.info(f"Upstage parsing completed for {doc_id}/{version_id}")
            # Download and normalize
            parse_upstage_download.delay(doc_id, version_id, request_id)

        elif status == "failed":
            logger.error(f"Upstage parsing failed for {doc_id}/{version_id}")
            doc_version = (
                db.query(DocumentVersion)
                .filter_by(doc_id=doc_id, version_id=version_id)
                .first()
            )
            doc_version.status = "failed"
            doc_version.last_error = status_response.get("failure_message", "Unknown error")
            db.commit()

        else:
            # Still processing, schedule next poll with exponential backoff
            backoff = min(settings.upstage_poll_interval * (1.5 ** (attempt // 10)), 60)
            logger.info(f"Upstage still processing, retry in {backoff}s")
            parse_upstage_poll.apply_async(
                args=[doc_id, version_id, request_id, attempt + 1],
                countdown=int(backoff),
            )

    except Exception as e:
        logger.error(f"Error polling Upstage: {e}")
        # Retry with backoff
        backoff = min(settings.upstage_poll_interval * 2, 30)
        parse_upstage_poll.apply_async(
            args=[doc_id, version_id, request_id, attempt + 1],
            countdown=int(backoff),
        )

    finally:
        db.close()


@celery_app.task(name="app.tasks.parse_tasks.parse_upstage_download")
def parse_upstage_download(doc_id: str, version_id: str, request_id: str):
    """
    Download and normalize Upstage parsing results.

    Args:
        doc_id: Document ID
        version_id: Version ID
        request_id: Upstage request ID
    """
    db = SessionLocal()
    try:
        # Get final status with batch URLs
        logger.info(f"Downloading Upstage results for {doc_id}/{version_id}")
        status_response = upstage_parser.check_status(request_id)

        batches = status_response.get("batches", [])

        if not batches:
            raise ValueError("No batches in Upstage response")

        # Download all batch JSONs
        batches_data = []
        for batch in batches:
            download_url = batch.get("download_url")
            if download_url:
                logger.info(f"Downloading batch {batch.get('id')}")
                batch_json = upstage_parser.download_batch_json(download_url)
                batches_data.append(batch_json)

        if not batches_data:
            raise ValueError("No batch data downloaded")

        # Normalize to our schema
        logger.info(f"Normalizing Upstage data for {doc_id}/{version_id}")
        normalized_json = upstage_parser.normalize_upstage_json(
            batches_data, doc_id, version_id
        )

        # Upload to MinIO
        logger.info(f"Uploading normalized JSON for {doc_id}/{version_id}")
        json_uri = minio_service.upload_json(doc_id, version_id, normalized_json)

        # Update status
        doc_version = (
            db.query(DocumentVersion)
            .filter_by(doc_id=doc_id, version_id=version_id)
            .first()
        )
        doc_version.status = "parsed"
        doc_version.result_json_uri = json_uri
        doc_version.updated_at = datetime.utcnow()
        db.commit()

        logger.info(f"Successfully processed Upstage results for {doc_id}/{version_id}")

        # Trigger indexing
        from app.tasks.index_tasks import index_document
        index_document.delay(doc_id, version_id)

    except Exception as e:
        logger.error(f"Error downloading Upstage results: {e}")
        doc_version = (
            db.query(DocumentVersion)
            .filter_by(doc_id=doc_id, version_id=version_id)
            .first()
        )
        doc_version.status = "failed"
        doc_version.last_error = str(e)
        db.commit()
        raise

    finally:
        db.close()
