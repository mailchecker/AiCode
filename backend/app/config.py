"""Application configuration management."""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MinIO Configuration
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False

    # MinIO Buckets
    bucket_raw_pdf: str = "raw-pdf"
    bucket_parsed_json: str = "parsed-json"
    bucket_derived: str = "derived"

    # Redis Configuration
    redis_url: str = "redis://redis:6379/0"

    # Elasticsearch Configuration
    elasticsearch_url: str = "http://elasticsearch:9200"
    elasticsearch_index: str = "textbook_chunks"

    # Database Configuration
    database_url: str = "sqlite:///./data/app.db"

    # Upstage API Configuration
    upstage_api_key: str = ""
    upstage_api_url: str = "https://api.upstage.ai/v1/document-digitization"
    upstage_poll_interval: int = 5  # seconds
    upstage_poll_max_attempts: int = 360  # 30 minutes max

    # OpenAI Configuration
    openai_api_key: str = ""

    # Embedding Configuration
    embedding_provider: Literal["kure", "openai", "e5", "bge"] = "kure"
    embedding_model: str = "nlpai-lab/KURE-v1"
    embedding_dimension: int = 768

    # Chunking Configuration
    chunk_size: int = 700
    chunk_overlap: int = 140
    min_chunk_size: int = 50  # Minimum tokens for a chunk
    chunk_by_sentence: bool = True  # Use sentence-based chunking
    merge_short_blocks: bool = True  # Merge blocks < min_chunk_size
    skip_metadata_blocks: bool = True  # Skip headers/footers

    # RAG Configuration
    top_k_retrieval: int = 5
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1000

    # Celery Configuration
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
