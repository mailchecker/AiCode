"""API endpoints for document management."""
import hashlib
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from app.database import get_db
from app.models import Document, DocumentVersion
from app.schemas import DocumentResponse, DocumentVersionResponse, UploadResponse, TaskStatus
from app.services.minio_service import minio_service
from app.tasks.parse_tasks import parse_local, parse_upstage_submit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    doc_id: Optional[str] = Form(None),
    version_id: Optional[str] = Form(None),
    parse_provider: str = Form("local"),
    db: Session = Depends(get_db),
):
    """
    Upload PDF document.

    Args:
        file: PDF file
        title: Document title
        doc_id: Document ID (auto-generated if not provided)
        version_id: Version ID (auto-generated if not provided)
        parse_provider: Parser to use ('local' or 'upstage')
        db: Database session

    Returns:
        Upload response with doc_id, version_id, and status
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Generate IDs if not provided
    if not doc_id:
        doc_id = str(uuid.uuid4())
    if not version_id:
        version_id = "v1"

    # Read PDF
    pdf_bytes = await file.read()

    # Calculate hash for idempotency
    pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()

    # Check if this exact document version already exists
    existing = (
        db.query(DocumentVersion)
        .filter_by(doc_id=doc_id, version_id=version_id, pdf_hash=pdf_hash)
        .first()
    )

    if existing:
        logger.info(f"Document {doc_id}/{version_id} already exists with same hash")
        return UploadResponse(
            doc_id=doc_id,
            version_id=version_id,
            status=existing.status,
            message="Document already exists",
        )

    # Upload to MinIO
    logger.info(f"Uploading PDF to MinIO: {doc_id}/{version_id}")
    pdf_uri = minio_service.upload_pdf(doc_id, version_id, pdf_bytes)

    # Create or update document
    document = db.query(Document).filter_by(doc_id=doc_id).first()
    if not document:
        document = Document(doc_id=doc_id, title=title, latest_version_id=version_id)
        db.add(document)
    else:
        document.latest_version_id = version_id

    # Create document version
    doc_version = DocumentVersion(
        doc_id=doc_id,
        version_id=version_id,
        pdf_uri=pdf_uri,
        pdf_hash=pdf_hash,
        parse_provider=parse_provider,
        status="uploaded",
    )
    db.add(doc_version)
    db.commit()

    logger.info(f"Created document version: {doc_id}/{version_id}")

    # Trigger parsing task
    if parse_provider == "local":
        parse_local.delay(doc_id, version_id)
    elif parse_provider == "upstage":
        parse_upstage_submit.delay(doc_id, version_id)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown parse provider: {parse_provider}")

    return UploadResponse(
        doc_id=doc_id,
        version_id=version_id,
        status="uploaded",
        message="Document uploaded and parsing started",
    )


@router.get("/", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    """List all documents."""
    documents = db.query(Document).all()
    return documents


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    """Get document by ID."""
    document = db.query(Document).filter_by(doc_id=doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/{doc_id}/versions", response_model=List[DocumentVersionResponse])
def list_versions(doc_id: str, db: Session = Depends(get_db)):
    """List all versions of a document."""
    versions = db.query(DocumentVersion).filter_by(doc_id=doc_id).all()
    return versions


@router.get("/{doc_id}/versions/{version_id}", response_model=DocumentVersionResponse)
def get_version(doc_id: str, version_id: str, db: Session = Depends(get_db)):
    """Get specific document version."""
    version = (
        db.query(DocumentVersion)
        .filter_by(doc_id=doc_id, version_id=version_id)
        .first()
    )
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.get("/{doc_id}/versions/{version_id}/status", response_model=TaskStatus)
def get_status(doc_id: str, version_id: str, db: Session = Depends(get_db)):
    """Get processing status of a document version."""
    version = (
        db.query(DocumentVersion)
        .filter_by(doc_id=doc_id, version_id=version_id)
        .first()
    )
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    return TaskStatus(
        doc_id=doc_id,
        version_id=version_id,
        status=version.status,
        progress=None,
        error=version.last_error,
    )


@router.delete("/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    """Delete document and all its versions."""
    document = db.query(Document).filter_by(doc_id=doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from database (cascade will delete versions)
    db.delete(document)
    db.commit()

    return {"message": f"Document {doc_id} deleted"}
