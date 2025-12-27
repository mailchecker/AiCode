"""API endpoints for RAG chat."""
from fastapi import APIRouter, HTTPException
import logging
from app.schemas import ChatRequest, ChatResponse, ChatSource
from app.services.rag.haystack_pipeline import rag_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Chat with RAG: retrieve + generate answer.

    Args:
        request: Chat request with query and filters

    Returns:
        Generated answer with sources
    """
    logger.info(f"Chat query: {request.query}")

    try:
        # Run RAG pipeline
        result = rag_pipeline.run(
            query=request.query,
            doc_id=request.doc_id,
            version_id=request.version_id,
            top_k=request.top_k,
        )

        # Convert to response schema
        sources = [
            ChatSource(
                doc_id=s["doc_id"],
                version_id=s["version_id"],
                page_start=s["page_start"],
                page_end=s["page_end"],
                text_snippet=s["text_snippet"],
            )
            for s in result["sources"]
        ]

        return ChatResponse(
            query=result["query"],
            answer=result["answer"],
            sources=sources,
            has_answer=result["has_answer"],
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
