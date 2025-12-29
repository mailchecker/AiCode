"""Upstage API PDF parser with async polling."""
import httpx
import time
import logging
import base64
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class UpstagePDFParser:
    """Upstage API-based PDF parser with async request/poll mechanism."""

    def __init__(self):
        """Initialize Upstage parser."""
        self.api_url = settings.upstage_api_url
        self.api_key = settings.upstage_api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def submit_parse_request(self, pdf_bytes: bytes, filename: str = "document.pdf") -> str:
        """
        Submit PDF to Upstage for async parsing.

        Args:
            pdf_bytes: PDF file bytes
            filename: Original filename

        Returns:
            request_id for polling
        """
        logger.info(f"Submitting PDF to Upstage API: {filename}")

        url = f"{self.api_url}/async"
        files = {"document": (filename, pdf_bytes, "application/pdf")}
        data = {
            "model": "document-parse",
            "ocr": "auto",
            "chart_recognition": True,
            "coordinates": True,
            "output_formats": '["html","markdown","text"]',
            "base64_encoding": '["figure"]',
        }

        try:
            with httpx.Client(timeout=120.0, follow_redirects=True) as client:
                response = client.post(url, headers=self.headers, files=files, data=data)
                response.raise_for_status()

                # Upstage returns request_id in JSON response
                result = response.json()
                # Try both 'request_id' and 'id' field names
                request_id = result.get("request_id") or result.get("id")

                if not request_id:
                    raise ValueError(f"No request_id in response: {result}")

                logger.info(f"Upstage parse request submitted: {request_id}")
                return request_id

        except Exception as e:
            logger.error(f"Error submitting to Upstage API: {e}")
            raise

    def check_status(self, request_id: str) -> Dict[str, Any]:
        """
        Check status of Upstage parse request.

        Args:
            request_id: Request ID from submission

        Returns:
            Status response with batches info
        """
        url = f"{self.api_url}/requests/{request_id}"

        try:
            with httpx.Client(timeout=60.0, follow_redirects=True) as client:
                response = client.get(url, headers=self.headers)
                response.raise_for_status()
                result = response.json()
                logger.debug(f"Upstage status for {request_id}: {result.get('status')}")
                return result

        except Exception as e:
            logger.error(f"Error checking Upstage status: {e}")
            raise

    def download_batch_json(self, download_url: str) -> Dict[str, Any]:
        """
        Download parsed JSON from batch download URL with retry logic.

        Args:
            download_url: Signed URL from batch result

        Returns:
            Parsed JSON data
        """
        import json
        from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1.5, min=1, max=10),
            retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
            reraise=True
        )
        def _download_with_retry():
            # Use streaming to handle large files efficiently
            with httpx.Client(timeout=120.0, follow_redirects=True) as client:
                with client.stream("GET", download_url) as response:
                    response.raise_for_status()

                    # Read response content in chunks (256KB like the original code)
                    content = b""
                    for chunk in response.iter_bytes(chunk_size=256 * 1024):
                        content += chunk

                    # Parse JSON
                    return json.loads(content.decode('utf-8'))

        try:
            return _download_with_retry()
        except Exception as e:
            logger.error(f"Error downloading batch JSON from {download_url}: {e}")
            raise

    def normalize_upstage_json(
        self,
        batches_data: List[Dict[str, Any]],
        doc_id: str,
        version_id: str,
        extract_images: bool = True,
    ) -> Dict[str, Any]:
        """
        Convert Upstage JSON format to our standard normalized schema.

        Args:
            batches_data: List of batch JSON data from Upstage
            doc_id: Document ID
            version_id: Version ID
            extract_images: If True, extract BASE64 images to MinIO (default: True)

        Returns:
            Normalized JSON in standard schema
        """
        logger.info(f"Normalizing {len(batches_data)} Upstage batches (extract_images={extract_images})")

        # Import here to avoid circular dependency
        from app.services.minio_service import minio_service

        pages = []
        total_images = 0

        # Each batch file is a single page
        for batch_data in batches_data:
            # Upstage format: Each batch file contains data for one page
            # Check if batch has "pages" array (multi-page batch) or is a single page
            if "pages" in batch_data:
                batch_pages = batch_data["pages"]
            else:
                # Single page batch - wrap it in a list
                batch_pages = [batch_data]

            for page_data in batch_pages:
                # Extract elements from page
                elements = page_data.get("elements", [])

                # Group elements by page number (each element has its own page field)
                pages_dict = {}
                for element in elements:
                    page_no = element.get("page", 1)
                    if page_no not in pages_dict:
                        pages_dict[page_no] = []

                    element_type = element.get("category", "body")
                    element_id = element.get("id", 0)

                    # Text is inside content object
                    content = element.get("content", {})

                    # For tables, prefer markdown to preserve structure
                    if element_type.lower() == "table":
                        text = content.get("markdown", content.get("text", "")).strip()
                    else:
                        text = content.get("text", "").strip()

                    block_type = self._map_element_type(element_type)

                    # Get bounding box - coordinates is already an array
                    bbox = self._extract_bbox(element.get("coordinates", []))

                    # Create base block - use id as order to preserve document order
                    block = {
                        "type": block_type,
                        "text": text,
                        "bbox": bbox,
                        "order": element_id,  # Use Upstage's id to preserve global order
                    }

                    # Handle images in figure blocks
                    if block_type == "figure" and extract_images:
                        base64_image = element.get("base64_encoding")
                        if base64_image:
                            try:
                                # Decode BASE64 image
                                image_data = base64.b64decode(base64_image)
                                image_type = self._detect_image_type(image_data)

                                # Upload to MinIO
                                image_id = f"page_{page_no}_element_{element_id}"
                                image_uri = minio_service.upload_image(
                                    doc_id=doc_id,
                                    version_id=version_id,
                                    image_data=image_data,
                                    image_id=image_id,
                                    content_type=image_type,
                                )

                                # Add image URI to block
                                block["image_uri"] = image_uri
                                block["image_type"] = image_type
                                block["image_size"] = len(image_data)
                                total_images += 1

                                logger.debug(f"Extracted image: {image_uri} ({len(image_data)} bytes)")

                            except Exception as e:
                                logger.error(f"Error extracting image from page {page_no}, block {idx}: {e}")
                                # Continue without image
                                block["image_error"] = str(e)

                    # Only add blocks with content or images
                    if text or block.get("image_uri"):
                        pages_dict[page_no].append(block)

                # Convert pages_dict to pages list
                for page_no in sorted(pages_dict.keys()):
                    page_blocks = pages_dict[page_no]
                    # Blocks already have order from element id - preserve it
                    pages.append({
                        "page_no": page_no,
                        "blocks": page_blocks,
                    })

        # Sort pages by page number
        pages.sort(key=lambda p: p["page_no"])

        result = {
            "doc_id": doc_id,
            "version_id": version_id,
            "pages": pages,
        }

        logger.info(f"Normalized {len(pages)} pages with {total_images} images from Upstage data")
        return result

    def _extract_bbox(self, points: Optional[List]) -> Optional[List[float]]:
        """
        Extract bounding box from Upstage coordinate points.

        Args:
            points: Upstage coordinate points [{"x": x1, "y": y1}, {"x": x2, "y": y2}, ...]

        Returns:
            Bounding box [x1, y1, x2, y2] or None
        """
        if not points or not isinstance(points, list):
            return None

        # Upstage returns [{"x": x1, "y": y1}, {"x": x2, "y": y2}, ...]
        # Convert to [x1, y1, x2, y2] (top-left, bottom-right)
        if len(points) >= 2:
            x_coords = [p.get("x") for p in points if isinstance(p, dict) and "x" in p]
            y_coords = [p.get("y") for p in points if isinstance(p, dict) and "y" in p]
            if x_coords and y_coords:
                return [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]

        return None

    def _detect_image_type(self, image_data: bytes) -> str:
        """
        Detect image MIME type from image bytes using magic numbers.

        Args:
            image_data: Image binary data

        Returns:
            MIME type (e.g., "image/png", "image/jpeg")
        """
        if len(image_data) < 12:
            return "image/png"  # Default

        # PNG: 89 50 4E 47
        if image_data[:4] == b'\x89PNG':
            return "image/png"

        # JPEG: FF D8 FF
        if image_data[:3] == b'\xff\xd8\xff':
            return "image/jpeg"

        # GIF: 47 49 46 38
        if image_data[:4] in (b'GIF87a', b'GIF89a'):
            return "image/gif"

        # WebP: 52 49 46 46 ... 57 45 42 50
        if image_data[:4] == b'RIFF' and image_data[8:12] == b'WEBP':
            return "image/webp"

        # Default to PNG
        return "image/png"

    def _map_element_type(self, upstage_type: str) -> str:
        """
        Map Upstage element category to our block types.

        Upstage categories (from HTML output):
        - table: <table> .. </table>
        - figure: <figure><img> .. </img></figure>
        - chart: <figure><img data-category="chart"> .. </img></figure>
        - heading1: <h1>... </h1>
        - header: <header> .. </header> (page header - metadata)
        - footer: <footer> .. </footer> (page footer - metadata)
        - caption: <caption> .. </caption>
        - paragraph: <p data-category="paragraph">..</p>
        - equation: <p data-category="equation">..</p>
        - list: <p data-category="list">..</p>
        - index: <p data-category="index">..</p>
        - footnote: <p data-category="footnote"> </p>

        Args:
            upstage_type: Upstage element category

        Returns:
            Our block type
        """
        type_mapping = {
            # Tables and figures
            "table": "table",
            "figure": "figure",
            "chart": "figure",  # Chart is a type of figure

            # Headings
            "heading1": "heading",
            "heading2": "heading",
            "heading3": "heading",
            "heading4": "heading",
            "heading5": "heading",
            "heading6": "heading",

            # Content blocks
            "paragraph": "body",
            "list": "body",
            "equation": "equation",  # Keep separate for special handling
            "footnote": "footnote",  # Keep separate for reference
            "caption": "caption",

            # Metadata (page headers/footers - not section headers)
            "header": "metadata",  # Page header
            "footer": "metadata",  # Page footer
            "index": "metadata",   # Index entries
        }
        return type_mapping.get(upstage_type.lower(), "body")


# Global instance
upstage_parser = UpstagePDFParser()
