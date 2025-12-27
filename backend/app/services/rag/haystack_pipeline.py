"""Haystack-based RAG pipeline."""
from typing import Dict, Any, Optional, List
import logging
from app.services.elasticsearch_service import elasticsearch_service
from app.services.llm_service import llm_service
from app.config import settings

logger = logging.getLogger(__name__)


class HaystackRAGPipeline:
    """RAG pipeline using Haystack architecture."""

    def __init__(self):
        """Initialize RAG pipeline."""
        self.es_service = elasticsearch_service
        self.llm_service = llm_service
        self.top_k = settings.top_k_retrieval

    def run(
        self,
        query: str,
        doc_id: Optional[str] = None,
        version_id: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Run RAG pipeline: retrieve + generate.

        Args:
            query: User question
            doc_id: Filter by document ID
            version_id: Filter by version ID
            top_k: Number of contexts to retrieve

        Returns:
            Dict with answer, sources, and metadata
        """
        logger.info(f"Running RAG pipeline for query: {query[:50]}...")

        # Use provided top_k or default
        k = top_k or self.top_k

        # Step 1: Retrieve relevant contexts using hybrid search
        contexts = self.es_service.search_hybrid(
            query=query,
            doc_id=doc_id,
            version_id=version_id,
            top_k=k,
        )

        if not contexts:
            logger.warning(f"No contexts found for query: {query}")
            return {
                "query": query,
                "answer": "죄송합니다. 질문과 관련된 내용을 교재에서 찾을 수 없습니다.",
                "sources": [],
                "has_answer": False,
            }

        # Step 2: Generate answer using LLM
        llm_result = self.llm_service.generate_answer(query, contexts)

        # Step 3: Prepare sources
        sources = []
        for ctx in contexts:
            sources.append({
                "doc_id": ctx["doc_id"],
                "version_id": ctx["version_id"],
                "page_start": ctx["page_start"],
                "page_end": ctx["page_end"],
                "text_snippet": ctx["text"][:200] + "..." if len(ctx["text"]) > 200 else ctx["text"],
            })

        return {
            "query": query,
            "answer": llm_result["answer"],
            "sources": sources,
            "has_answer": llm_result["has_answer"],
        }

    def retrieve_only(
        self,
        query: str,
        doc_id: Optional[str] = None,
        version_id: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve contexts without generation.

        Args:
            query: Search query
            doc_id: Filter by document ID
            version_id: Filter by version ID
            top_k: Number of results

        Returns:
            List of retrieved contexts
        """
        k = top_k or self.top_k

        contexts = self.es_service.search_hybrid(
            query=query,
            doc_id=doc_id,
            version_id=version_id,
            top_k=k,
        )

        return contexts


# Global instance
rag_pipeline = HaystackRAGPipeline()
