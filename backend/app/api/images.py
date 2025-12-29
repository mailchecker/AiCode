"""Image retrieval API endpoints."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.services.minio_service import minio_service
import logging
import io

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/images", tags=["images"])


@router.get("/{doc_id}/{version_id}/images/{image_filename}")
async def get_image(doc_id: str, version_id: str, image_filename: str):
    """
    Retrieve image file from MinIO.

    Args:
        doc_id: Document ID
        version_id: Version ID
        image_filename: Image filename (e.g., "page_1_block_3.png")

    Returns:
        Image file as StreamingResponse

    Example:
        GET /api/images/doc_123/v1/images/page_1_block_3.png
    """
    try:
        # Construct MinIO URI
        uri = f"bucket-derived/{doc_id}/{version_id}/images/{image_filename}"

        # Download image
        image_data = minio_service.download_file(uri)

        # Determine MIME type
        if image_filename.endswith('.png'):
            media_type = "image/png"
        elif image_filename.endswith(('.jpg', '.jpeg')):
            media_type = "image/jpeg"
        elif image_filename.endswith('.gif'):
            media_type = "image/gif"
        elif image_filename.endswith('.webp'):
            media_type = "image/webp"
        else:
            media_type = "application/octet-stream"

        return StreamingResponse(
            io.BytesIO(image_data),
            media_type=media_type
        )

    except Exception as e:
        logger.error(f"Error retrieving image {uri}: {e}")
        raise HTTPException(status_code=404, detail="Image not found")


@router.get("/{doc_id}/{version_id}/images/{image_filename}/url")
async def get_image_presigned_url(
    doc_id: str,
    version_id: str,
    image_filename: str,
    expires: int = 3600
):
    """
    Generate presigned URL for image access.

    Args:
        doc_id: Document ID
        version_id: Version ID
        image_filename: Image filename
        expires: URL expiration time in seconds (default: 3600 = 1 hour)

    Returns:
        JSON with presigned URL and expiration time

    Example:
        GET /api/images/doc_123/v1/images/page_1_block_3.png/url?expires=7200

        Response:
        {
            "url": "http://minio:9000/bucket-derived/...?X-Amz-Algorithm=...",
            "expires_in": 7200
        }
    """
    try:
        uri = f"bucket-derived/{doc_id}/{version_id}/images/{image_filename}"
        presigned_url = minio_service.get_presigned_url(uri, expires_seconds=expires)

        return {
            "url": presigned_url,
            "expires_in": expires
        }

    except Exception as e:
        logger.error(f"Error generating presigned URL for {uri}: {e}")
        raise HTTPException(status_code=404, detail="Image not found")
