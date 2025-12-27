"""SQLAlchemy database models."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Document(Base):
    """Document metadata table."""

    __tablename__ = "documents"

    doc_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    latest_version_id = Column(String, nullable=True)

    # Relationship
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")


class DocumentVersion(Base):
    """Document version table for tracking parsing and indexing status."""

    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, ForeignKey("documents.doc_id"), nullable=False, index=True)
    version_id = Column(String, nullable=False, index=True)
    pdf_uri = Column(String, nullable=False)  # MinIO URI
    pdf_hash = Column(String, nullable=False, index=True)  # SHA256 hash for idempotency

    # Parsing configuration
    parse_provider = Column(String, nullable=False)  # 'local' | 'upstage'
    parse_request_id = Column(String, nullable=True)  # For async external parsing

    # Status tracking
    status = Column(
        String,
        nullable=False,
        default="uploaded",
        # uploaded | parsing | parsed | indexing | indexed | failed
    )

    # Results
    result_json_uri = Column(String, nullable=True)  # MinIO URI for normalized JSON

    # Error handling
    attempt_count = Column(Integer, default=0, nullable=False)
    last_error = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    document = relationship("Document", back_populates="versions")

    # Composite unique index for idempotency
    __table_args__ = (
        Index("idx_doc_version_hash", "doc_id", "version_id", "pdf_hash", unique=True),
    )
