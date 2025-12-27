"""Text chunking utilities."""
import tiktoken
from typing import List, Dict, Any
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class TextChunker:
    """Service for chunking text documents."""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize text chunker.

        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        # Initialize tokenizer (using tiktoken for accurate token counting)
        try:
            self.encoding = tiktoken.encoding_for_model("gpt-4")
        except:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def chunk_normalized_json(self, normalized_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk normalized JSON document into smaller pieces.

        Args:
            normalized_json: Normalized document JSON

        Returns:
            List of chunks with metadata
        """
        doc_id = normalized_json["doc_id"]
        version_id = normalized_json["version_id"]
        pages = normalized_json["pages"]

        chunks = []
        chunk_id_counter = 0

        for page in pages:
            page_no = page["page_no"]
            blocks = page["blocks"]

            # Filter out headers and footers
            body_blocks = [b for b in blocks if b["type"] not in ["header", "footer"]]

            if not body_blocks:
                continue

            # Combine blocks into page text
            page_text = " ".join([b["text"] for b in body_blocks])

            # Chunk the page text
            page_chunks = self._chunk_text(page_text)

            for chunk_text in page_chunks:
                chunks.append({
                    "chunk_id": f"{doc_id}_{version_id}_{chunk_id_counter}",
                    "doc_id": doc_id,
                    "version_id": version_id,
                    "text": chunk_text,
                    "page_start": page_no,
                    "page_end": page_no,
                    "section_path": None,
                    "source_type": "body",
                })
                chunk_id_counter += 1

        logger.info(f"Created {len(chunks)} chunks from {len(pages)} pages")
        return chunks

    def _chunk_text(self, text: str) -> List[str]:
        """
        Chunk text into smaller pieces with overlap.

        Args:
            text: Input text

        Returns:
            List of text chunks
        """
        if not text.strip():
            return []

        # Tokenize
        tokens = self.encoding.encode(text)

        if len(tokens) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]

            # Decode back to text
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)

            # Move start by (chunk_size - overlap)
            start += self.chunk_size - self.chunk_overlap

        return chunks


# Global instance
text_chunker = TextChunker()
