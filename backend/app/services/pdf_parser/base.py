"""Base classes for PDF parsing."""
from abc import ABC, abstractmethod
from typing import Dict, Any


class PDFParser(ABC):
    """Abstract base class for PDF parsers."""

    @abstractmethod
    def parse(self, pdf_bytes: bytes, doc_id: str, version_id: str) -> Dict[str, Any]:
        """
        Parse PDF and return normalized JSON.

        Args:
            pdf_bytes: PDF file bytes
            doc_id: Document ID
            version_id: Version ID

        Returns:
            Normalized JSON in standard schema format
        """
        pass
