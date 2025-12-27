"""Embedding service with pluggable providers."""
from abc import ABC, abstractmethod
from typing import List
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query.

        Args:
            text: Query text to embed

        Returns:
            Embedding vector
        """
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        pass


class KUREEmbeddingProvider(EmbeddingProvider):
    """KURE-v1 embedding provider using sentence-transformers."""

    def __init__(self, model_name: str = "nlpai-lab/KURE-v1"):
        """Initialize KURE embedding model."""
        from sentence_transformers import SentenceTransformer

        logger.info(f"Loading KURE model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"KURE model loaded with dimension: {self.dimension}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents using KURE."""
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed query using KURE."""
        embedding = self.model.encode([text], show_progress_bar=False, convert_to_numpy=True)
        return embedding[0].tolist()

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider."""

    def __init__(self, model_name: str = "text-embedding-3-small"):
        """Initialize OpenAI embedding."""
        from openai import OpenAI

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_name = model_name

        # Model dimensions
        self.dimension_map = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        self.dimension = self.dimension_map.get(model_name, 1536)
        logger.info(f"OpenAI embedding initialized: {model_name}, dimension: {self.dimension}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents using OpenAI."""
        response = self.client.embeddings.create(input=texts, model=self.model_name)
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> List[float]:
        """Embed query using OpenAI."""
        response = self.client.embeddings.create(input=[text], model=self.model_name)
        return response.data[0].embedding

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension


class E5EmbeddingProvider(EmbeddingProvider):
    """E5 embedding provider using sentence-transformers."""

    def __init__(self, model_name: str = "intfloat/multilingual-e5-large"):
        """Initialize E5 embedding model."""
        from sentence_transformers import SentenceTransformer

        logger.info(f"Loading E5 model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"E5 model loaded with dimension: {self.dimension}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents using E5."""
        # E5 models require "passage: " prefix for documents
        prefixed_texts = [f"passage: {text}" for text in texts]
        embeddings = self.model.encode(prefixed_texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed query using E5."""
        # E5 models require "query: " prefix for queries
        prefixed_text = f"query: {text}"
        embedding = self.model.encode([prefixed_text], show_progress_bar=False, convert_to_numpy=True)
        return embedding[0].tolist()

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension


class BGEEmbeddingProvider(EmbeddingProvider):
    """BGE embedding provider using sentence-transformers."""

    def __init__(self, model_name: str = "BAAI/bge-m3"):
        """Initialize BGE embedding model."""
        from sentence_transformers import SentenceTransformer

        logger.info(f"Loading BGE model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"BGE model loaded with dimension: {self.dimension}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents using BGE."""
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed query using BGE."""
        embedding = self.model.encode([text], show_progress_bar=False, convert_to_numpy=True)
        return embedding[0].tolist()

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension


class EmbeddingService:
    """Service for managing embeddings with pluggable providers."""

    def __init__(self):
        """Initialize embedding service with configured provider."""
        self.provider = self._create_provider()

    def _create_provider(self) -> EmbeddingProvider:
        """Create embedding provider based on configuration."""
        provider_type = settings.embedding_provider.lower()

        if provider_type == "kure":
            return KUREEmbeddingProvider(settings.embedding_model)
        elif provider_type == "openai":
            return OpenAIEmbeddingProvider(settings.embedding_model)
        elif provider_type == "e5":
            return E5EmbeddingProvider(settings.embedding_model)
        elif provider_type == "bge":
            return BGEEmbeddingProvider(settings.embedding_model)
        else:
            raise ValueError(f"Unknown embedding provider: {provider_type}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents."""
        return self.provider.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed query."""
        return self.provider.embed_query(text)

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.provider.get_dimension()


# Global instance (lazy loaded)
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get global embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
