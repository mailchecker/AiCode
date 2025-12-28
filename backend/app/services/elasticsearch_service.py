"""Elasticsearch service for indexing and searching."""
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from typing import List, Dict, Any, Optional
import logging
from app.config import settings
from app.services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """Service for Elasticsearch operations."""

    def __init__(self):
        """Initialize Elasticsearch client."""
        self.client = Elasticsearch([settings.elasticsearch_url])
        self.index_name = settings.elasticsearch_index
        self.embedding_service = get_embedding_service()
        self._ensure_index()

    def _ensure_index(self):
        """Ensure index exists with proper mappings."""
        try:
            if self.client.indices.exists(index=self.index_name):
                logger.info(f"Index {self.index_name} already exists")
                return

            # Get embedding dimension from service
            embedding_dim = self.embedding_service.get_dimension()

            # Index mappings
            mappings = {
                "properties": {
                    "chunk_id": {"type": "keyword"},
                    "doc_id": {"type": "keyword"},
                    "version_id": {"type": "keyword"},
                    "text": {"type": "text", "analyzer": "standard"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": embedding_dim,
                        "index": True,
                        "similarity": "cosine",
                    },
                    "page_start": {"type": "integer"},
                    "page_end": {"type": "integer"},
                    "section_path": {"type": "keyword"},
                    "source_type": {"type": "keyword"},
                    "created_at": {"type": "date"},
                }
            }

            self.client.indices.create(index=self.index_name, mappings=mappings)
            logger.info(f"Created index {self.index_name} with embedding dimension {embedding_dim}")

        except Exception as e:
            # Handle race condition where index was created between check and create
            if "resource_already_exists_exception" in str(e):
                logger.info(f"Index {self.index_name} was created by another process")
            else:
                logger.error(f"Error ensuring index: {e}")
                raise

    def index_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Bulk index chunks to Elasticsearch.

        Args:
            chunks: List of chunk dictionaries with text and metadata
        """
        if not chunks:
            logger.warning("No chunks to index")
            return

        logger.info(f"Indexing {len(chunks)} chunks")

        # Generate embeddings for all chunks
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_service.embed_documents(texts)

        # Prepare bulk actions
        actions = []
        for chunk, embedding in zip(chunks, embeddings):
            action = {
                "_index": self.index_name,
                "_id": chunk["chunk_id"],
                "_source": {
                    "chunk_id": chunk["chunk_id"],
                    "doc_id": chunk["doc_id"],
                    "version_id": chunk["version_id"],
                    "text": chunk["text"],
                    "embedding": embedding,
                    "page_start": chunk["page_start"],
                    "page_end": chunk["page_end"],
                    "section_path": chunk.get("section_path"),
                    "source_type": chunk.get("source_type", "body"),
                    "created_at": chunk.get("created_at"),
                },
            }
            actions.append(action)

        # Bulk index
        success, failed = bulk(self.client, actions, raise_on_error=False)
        logger.info(f"Indexed {success} chunks, {len(failed)} failed")

        if failed:
            logger.error(f"Failed chunks: {failed}")

    def search_bm25(
        self,
        query: str,
        doc_id: Optional[str] = None,
        version_id: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search using BM25 (keyword search).

        Args:
            query: Search query
            doc_id: Filter by document ID
            version_id: Filter by version ID
            top_k: Number of results

        Returns:
            List of search results
        """
        must_clauses = [{"match": {"text": query}}]

        if doc_id:
            must_clauses.append({"term": {"doc_id": doc_id}})
        if version_id:
            must_clauses.append({"term": {"version_id": version_id}})

        search_body = {
            "query": {"bool": {"must": must_clauses}},
            "size": top_k,
        }

        response = self.client.search(index=self.index_name, body=search_body)

        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            results.append({
                "chunk_id": source["chunk_id"],
                "doc_id": source["doc_id"],
                "version_id": source["version_id"],
                "text": source["text"],
                "page_start": source["page_start"],
                "page_end": source["page_end"],
                "section_path": source.get("section_path"),
                "score": hit["_score"],
            })

        return results

    def search_vector(
        self,
        query: str,
        doc_id: Optional[str] = None,
        version_id: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search using vector similarity.

        Args:
            query: Search query
            doc_id: Filter by document ID
            version_id: Filter by version ID
            top_k: Number of results

        Returns:
            List of search results
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)

        # Build filter
        filter_clauses = []
        if doc_id:
            filter_clauses.append({"term": {"doc_id": doc_id}})
        if version_id:
            filter_clauses.append({"term": {"version_id": version_id}})

        search_body = {
            "query": {
                "script_score": {
                    "query": {"bool": {"must": filter_clauses}} if filter_clauses else {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": query_embedding},
                    },
                }
            },
            "size": top_k,
        }

        response = self.client.search(index=self.index_name, body=search_body)

        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            results.append({
                "chunk_id": source["chunk_id"],
                "doc_id": source["doc_id"],
                "version_id": source["version_id"],
                "text": source["text"],
                "page_start": source["page_start"],
                "page_end": source["page_end"],
                "section_path": source.get("section_path"),
                "score": hit["_score"],
            })

        return results

    def search_hybrid(
        self,
        query: str,
        doc_id: Optional[str] = None,
        version_id: Optional[str] = None,
        top_k: int = 5,
        bm25_weight: float = 0.3,
        vector_weight: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining BM25 and vector search.

        Args:
            query: Search query
            doc_id: Filter by document ID
            version_id: Filter by version ID
            top_k: Number of results
            bm25_weight: Weight for BM25 score
            vector_weight: Weight for vector score

        Returns:
            List of search results
        """
        # Get results from both methods
        bm25_results = self.search_bm25(query, doc_id, version_id, top_k * 2)
        vector_results = self.search_vector(query, doc_id, version_id, top_k * 2)

        # Combine and re-rank
        combined = {}

        for result in bm25_results:
            chunk_id = result["chunk_id"]
            combined[chunk_id] = result.copy()
            combined[chunk_id]["score"] = result["score"] * bm25_weight

        for result in vector_results:
            chunk_id = result["chunk_id"]
            if chunk_id in combined:
                combined[chunk_id]["score"] += result["score"] * vector_weight
            else:
                combined[chunk_id] = result.copy()
                combined[chunk_id]["score"] = result["score"] * vector_weight

        # Sort by combined score
        results = sorted(combined.values(), key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def delete_by_doc_version(self, doc_id: str, version_id: str):
        """
        Delete all chunks for a specific document version.

        Args:
            doc_id: Document ID
            version_id: Version ID
        """
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"doc_id": doc_id}},
                        {"term": {"version_id": version_id}},
                    ]
                }
            }
        }

        self.client.delete_by_query(index=self.index_name, body=query)
        logger.info(f"Deleted chunks for {doc_id}/{version_id}")


# Global instance
elasticsearch_service = ElasticsearchService()
