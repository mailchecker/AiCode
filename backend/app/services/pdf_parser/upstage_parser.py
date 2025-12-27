"""Upstage API PDF parser with async polling."""
import httpx
import time
import logging
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
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, headers=self.headers, files=files, data=data)
                response.raise_for_status()

                # Upstage returns request_id in JSON response
                result = response.json()
                request_id = result.get("id")

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
            with httpx.Client(timeout=30.0) as client:
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
        Download parsed JSON from batch download URL.

        Args:
            download_url: Signed URL from batch result

        Returns:
            Parsed JSON data
        """
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.get(download_url)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Error downloading batch JSON: {e}")
            raise

    def normalize_upstage_json(self, batches_data: List[Dict[str, Any]], doc_id: str, version_id: str) -> Dict[str, Any]:
        """
        Convert Upstage JSON format to our standard normalized schema.

        Args:
            batches_data: List of batch JSON data from Upstage
            doc_id: Document ID
            version_id: Version ID

        Returns:
            Normalized JSON in standard schema
        """
        logger.info(f"Normalizing {len(batches_data)} Upstage batches")

        pages = []

        # Each batch contains multiple pages
        for batch_data in batches_data:
            # Upstage format: { "content": { "html": ..., "markdown": ..., "text": ... }, "pages": [...] }
            batch_pages = batch_data.get("pages", [])

            for page_data in batch_pages:
                page_no = page_data.get("page", 0)

                # Extract elements from page
                elements = page_data.get("elements", [])
                blocks = []

                for idx, element in enumerate(elements):
                    element_type = element.get("category", "body")
                    text = element.get("text", "").strip()

                    if not text:
                        continue

                    # Map Upstage categories to our types
                    block_type = self._map_element_type(element_type)

                    # Get bounding box
                    bbox = element.get("coordinates", {}).get("points", None)
                    if bbox and isinstance(bbox, list):
                        # Upstage returns [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                        # Convert to [x1, y1, x2, y2] (top-left, bottom-right)
                        if len(bbox) >= 2:
                            x_coords = [p[0] for p in bbox if len(p) >= 2]
                            y_coords = [p[1] for p in bbox if len(p) >= 2]
                            if x_coords and y_coords:
                                bbox = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]
                            else:
                                bbox = None
                        else:
                            bbox = None

                    blocks.append({
                        "type": block_type,
                        "text": text,
                        "bbox": bbox,
                        "order": idx,
                    })

                pages.append({
                    "page_no": page_no,
                    "blocks": blocks,
                })

        # Sort pages by page number
        pages.sort(key=lambda p: p["page_no"])

        result = {
            "doc_id": doc_id,
            "version_id": version_id,
            "pages": pages,
        }

        logger.info(f"Normalized {len(pages)} pages from Upstage data")
        return result

    def _map_element_type(self, upstage_type: str) -> str:
        """
        Map Upstage element category to our block types.

        Args:
            upstage_type: Upstage element category

        Returns:
            Our block type
        """
        type_mapping = {
            "header": "header",
            "footer": "footer",
            "table": "table",
            "figure": "figure",
            "caption": "caption",
            "paragraph": "body",
            "text": "body",
            "list": "body",
            "heading": "body",
        }
        return type_mapping.get(upstage_type.lower(), "body")


# Global instance
upstage_parser = UpstagePDFParser()
