"""API endpoints for search."""
from fastapi import APIRouter, HTTPException
import logging
from app.schemas import SearchRequest, SearchResponse, SearchResultItem
from app.services.elasticsearch_service import elasticsearch_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/", response_model=SearchResponse)
def search(request: SearchRequest):
    """
    Search documents using hybrid BM25 + Vector search.

    Args:
        request: Search request with query and filters

    Returns:
        Search results with scores
    """
    logger.info(f"Search query: {request.query}")

    try:
        # Perform hybrid search
        results = elasticsearch_service.search_hybrid(
            query=request.query,
            doc_id=request.doc_id,
            version_id=request.version_id,
            top_k=request.top_k,
        )

        # Convert to response schema
        result_items = [
            SearchResultItem(
                chunk_id=r["chunk_id"],
                doc_id=r["doc_id"],
                version_id=r["version_id"],
                text=r["text"],
                page_start=r["page_start"],
                page_end=r["page_end"],
                section_path=r.get("section_path"),
                score=r["score"],
            )
            for r in results
        ]

        return SearchResponse(
            query=request.query,
            results=result_items,
            total=len(result_items),
        )

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/bm25", response_model=SearchResponse)
def search_bm25(request: SearchRequest):
    """Search using BM25 only."""
    logger.info(f"BM25 search query: {request.query}")

    try:
        results = elasticsearch_service.search_bm25(
            query=request.query,
            doc_id=request.doc_id,
            version_id=request.version_id,
            top_k=request.top_k,
        )

        result_items = [
            SearchResultItem(
                chunk_id=r["chunk_id"],
                doc_id=r["doc_id"],
                version_id=r["version_id"],
                text=r["text"],
                page_start=r["page_start"],
                page_end=r["page_end"],
                section_path=r.get("section_path"),
                score=r["score"],
            )
            for r in results
        ]

        return SearchResponse(
            query=request.query,
            results=result_items,
            total=len(result_items),
        )

    except Exception as e:
        logger.error(f"BM25 search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/vector", response_model=SearchResponse)
def search_vector(request: SearchRequest):
    """Search using vector similarity only."""
    logger.info(f"Vector search query: {request.query}")

    try:
        results = elasticsearch_service.search_vector(
            query=request.query,
            doc_id=request.doc_id,
            version_id=request.version_id,
            top_k=request.top_k,
        )

        result_items = [
            SearchResultItem(
                chunk_id=r["chunk_id"],
                doc_id=r["doc_id"],
                version_id=r["version_id"],
                text=r["text"],
                page_start=r["page_start"],
                page_end=r["page_end"],
                section_path=r.get("section_path"),
                score=r["score"],
            )
            for r in results
        ]

        return SearchResponse(
            query=request.query,
            results=result_items,
            total=len(result_items),
        )

    except Exception as e:
        logger.error(f"Vector search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
