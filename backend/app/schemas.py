"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


# Document Schemas
class DocumentCreate(BaseModel):
    """Schema for creating a new document."""

    title: str
    doc_id: Optional[str] = None  # Auto-generated if not provided


class DocumentResponse(BaseModel):
    """Schema for document response."""

    doc_id: str
    title: str
    created_at: datetime
    latest_version_id: Optional[str] = None

    class Config:
        from_attributes = True


# Document Version Schemas
class DocumentVersionCreate(BaseModel):
    """Schema for creating a new document version."""

    doc_id: str
    version_id: str
    parse_provider: Literal["local", "upstage"] = "local"


class DocumentVersionResponse(BaseModel):
    """Schema for document version response."""

    id: int
    doc_id: str
    version_id: str
    pdf_uri: str
    pdf_hash: str
    parse_provider: str
    parse_request_id: Optional[str] = None
    status: str
    result_json_uri: Optional[str] = None
    attempt_count: int
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Upload Schemas
class UploadResponse(BaseModel):
    """Schema for upload response."""

    doc_id: str
    version_id: str
    status: str
    message: str


# Normalized JSON Schema (Standard Format)
class BlockSchema(BaseModel):
    """Schema for a text block in a page."""

    type: Literal["body", "header", "footer", "table", "figure", "caption"]
    text: str
    bbox: Optional[List[float]] = None  # [x1, y1, x2, y2]
    order: int


class PageSchema(BaseModel):
    """Schema for a page in the document."""

    page_no: int
    blocks: List[BlockSchema]


class NormalizedDocumentSchema(BaseModel):
    """Standard normalized document schema."""

    doc_id: str
    version_id: str
    pages: List[PageSchema]


# Search Schemas
class SearchRequest(BaseModel):
    """Schema for search request."""

    query: str
    doc_id: Optional[str] = None
    version_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=50)


class SearchResultItem(BaseModel):
    """Schema for a single search result."""

    chunk_id: str
    doc_id: str
    version_id: str
    text: str
    page_start: int
    page_end: int
    section_path: Optional[str] = None
    score: float


class SearchResponse(BaseModel):
    """Schema for search response."""

    query: str
    results: List[SearchResultItem]
    total: int


# Chat Schemas
class ChatRequest(BaseModel):
    """Schema for chat request."""

    query: str
    doc_id: Optional[str] = None
    version_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)


class ChatSource(BaseModel):
    """Schema for chat answer source."""

    doc_id: str
    version_id: str
    page_start: int
    page_end: int
    text_snippet: str


class ChatResponse(BaseModel):
    """Schema for chat response."""

    query: str
    answer: str
    sources: List[ChatSource]
    has_answer: bool  # False if no relevant info found


# Status Schemas
class TaskStatus(BaseModel):
    """Schema for task status."""

    doc_id: str
    version_id: str
    status: str
    progress: Optional[str] = None
    error: Optional[str] = None
