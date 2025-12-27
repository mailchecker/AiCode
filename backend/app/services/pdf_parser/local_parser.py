"""Local PDF parser using PyMuPDF."""
import io
import re
import fitz  # PyMuPDF
from typing import Dict, Any, List
from app.services.pdf_parser.base import PDFParser
import logging

logger = logging.getLogger(__name__)


class LocalPDFParser(PDFParser):
    """Local PDF parser using PyMuPDF for text extraction."""

    def __init__(self):
        """Initialize local parser."""
        # Common header/footer patterns (page numbers, etc.)
        self.footer_patterns = [
            r"^\s*\d+\s*$",  # Just page number
            r"^\s*-\s*\d+\s*-\s*$",  # - 1 -
            r"^\s*Page\s+\d+\s*$",  # Page 1
            r"^\s*\d+\s*/\s*\d+\s*$",  # 1/10
        ]

    def _is_header_footer(self, text: str, y_position: float, page_height: float) -> str:
        """
        Determine if text is likely a header or footer.

        Args:
            text: Text content
            y_position: Y coordinate (0 is top)
            page_height: Page height

        Returns:
            'header', 'footer', or 'body'
        """
        # Check if in top 5% (header) or bottom 5% (footer)
        if y_position < page_height * 0.05:
            return "header"
        elif y_position > page_height * 0.95:
            return "footer"

        # Check footer patterns
        for pattern in self.footer_patterns:
            if re.match(pattern, text.strip()):
                return "footer"

        return "body"

    def parse(self, pdf_bytes: bytes, doc_id: str, version_id: str) -> Dict[str, Any]:
        """
        Parse PDF using PyMuPDF.

        Args:
            pdf_bytes: PDF file bytes
            doc_id: Document ID
            version_id: Version ID

        Returns:
            Normalized JSON in standard schema
        """
        logger.info(f"Starting local PDF parsing for {doc_id}/{version_id}")

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pages = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                page_dict = page.get_text("dict")
                page_height = page.rect.height

                blocks = []
                block_order = 0

                # Process each block in the page
                for block in page_dict.get("blocks", []):
                    if block.get("type") == 0:  # Text block
                        # Extract text from lines
                        text_parts = []
                        y_positions = []

                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                text_parts.append(span.get("text", ""))
                                # Get Y position from line bbox
                                y_positions.append(line.get("bbox", [0, 0, 0, 0])[1])

                        text = " ".join(text_parts).strip()
                        if not text:
                            continue

                        # Get average Y position
                        avg_y = sum(y_positions) / len(y_positions) if y_positions else 0

                        # Determine block type
                        block_type = self._is_header_footer(text, avg_y, page_height)

                        # Get bounding box
                        bbox = block.get("bbox", None)
                        if bbox:
                            bbox = list(bbox)

                        blocks.append({
                            "type": block_type,
                            "text": text,
                            "bbox": bbox,
                            "order": block_order,
                        })
                        block_order += 1

                pages.append({
                    "page_no": page_num + 1,
                    "blocks": blocks,
                })

            doc.close()

            result = {
                "doc_id": doc_id,
                "version_id": version_id,
                "pages": pages,
            }

            logger.info(f"Successfully parsed {len(pages)} pages locally")
            return result

        except Exception as e:
            logger.error(f"Error in local PDF parsing: {e}")
            raise
