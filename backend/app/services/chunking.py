"""Text chunking utilities with smart merging and sentence-based splitting."""
import tiktoken
from typing import List, Dict, Any
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Try to import kss for Korean sentence splitting
try:
    import kss
    KSS_AVAILABLE = True
except ImportError:
    KSS_AVAILABLE = False
    logger.warning("kss library not available. Sentence-based chunking will use basic fallback.")


class TextChunker:
    """Service for chunking text documents with smart merging and sentence splitting."""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize text chunker.

        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.min_chunk_size = settings.min_chunk_size
        self.max_embedding_tokens = settings.max_embedding_tokens
        self.chunk_by_sentence = settings.chunk_by_sentence
        self.merge_short_blocks = settings.merge_short_blocks
        self.skip_metadata_blocks = settings.skip_metadata_blocks

        # Initialize tokenizer (using tiktoken for accurate token counting)
        try:
            self.encoding = tiktoken.encoding_for_model("gpt-4")
        except:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if not text:
            return 0
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

            # Preprocess blocks: merge and filter
            processed_blocks = self._preprocess_blocks(blocks)

            if not processed_blocks:
                continue

            # Chunk the processed blocks
            page_chunks = self._chunk_blocks(processed_blocks)

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

    def _preprocess_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Preprocess blocks: skip metadata, merge short blocks.

        Args:
            blocks: List of blocks from a page

        Returns:
            Preprocessed blocks ready for chunking
        """
        if not blocks:
            return []

        processed = []
        merge_buffer = []
        merge_buffer_tokens = 0

        for block in blocks:
            block_type = block.get("type", "body")
            text = block.get("text", "").strip()

            if not text and not block.get("image_uri"):
                continue

            # Skip metadata blocks
            if self.skip_metadata_blocks and block_type in ["header", "footer"]:
                continue

            tokens = self.count_tokens(text)

            # Handle short blocks
            if self.merge_short_blocks and tokens < self.min_chunk_size:
                # Add to merge buffer
                merge_buffer.append(text)
                merge_buffer_tokens += tokens

                # Flush buffer if it reaches min size
                if merge_buffer_tokens >= self.min_chunk_size:
                    merged_text = "\n\n".join(merge_buffer)
                    processed.append({
                        "text": merged_text,
                        "type": "merged",
                        "tokens": merge_buffer_tokens
                    })
                    merge_buffer = []
                    merge_buffer_tokens = 0
            else:
                # Flush any pending buffer first
                if merge_buffer:
                    merged_text = "\n\n".join(merge_buffer)
                    processed.append({
                        "text": merged_text,
                        "type": "merged",
                        "tokens": merge_buffer_tokens
                    })
                    merge_buffer = []
                    merge_buffer_tokens = 0

                # Add current block
                processed.append({
                    "text": text,
                    "type": block_type,
                    "tokens": tokens,
                    "image_uri": block.get("image_uri"),
                    "image_type": block.get("image_type")
                })

        # Flush remaining buffer
        if merge_buffer:
            merged_text = "\n\n".join(merge_buffer)
            processed.append({
                "text": merged_text,
                "type": "merged",
                "tokens": merge_buffer_tokens
            })

        return processed

    def _chunk_blocks(self, blocks: List[Dict[str, Any]]) -> List[str]:
        """
        Chunk preprocessed blocks by accumulating them until chunk_size is reached.
        Respects Upstage paragraph boundaries - only splits if exceeds max_embedding_tokens.

        Args:
            blocks: Preprocessed blocks (each block is typically one Upstage paragraph)

        Returns:
            List of text chunks
        """
        chunks = []
        current_texts = []
        current_tokens = 0

        for block in blocks:
            # Clean text: replace newlines with spaces
            text = block["text"].replace("\n", " ").strip()
            tokens = self.count_tokens(text)

            # If single paragraph exceeds embedding limit, must split (unavoidable)
            if tokens > self.max_embedding_tokens:
                logger.warning(
                    f"Paragraph exceeds embedding limit ({tokens} > {self.max_embedding_tokens}). "
                    f"Splitting into sentences."
                )
                # Flush current accumulated texts first
                if current_texts:
                    chunks.append(" ".join(current_texts))
                    current_texts = []
                    current_tokens = 0

                # Split the oversized paragraph
                if self.chunk_by_sentence:
                    block_chunks = self._chunk_by_sentence(text)
                else:
                    block_chunks = self._chunk_by_token(text)
                chunks.extend(block_chunks)
                continue

            # Paragraph is within embedding limit - try to accumulate
            # Check if adding this paragraph exceeds target chunk_size
            if current_tokens + tokens > self.chunk_size:
                # Flush current chunk
                if current_texts:
                    chunks.append(" ".join(current_texts))

                # Start new chunk with this paragraph
                current_texts = [text]
                current_tokens = tokens
            else:
                # Add paragraph to current chunk
                current_texts.append(text)
                current_tokens += tokens

        # Flush remaining texts
        if current_texts:
            chunks.append(" ".join(current_texts))

        return chunks

    def _chunk_by_sentence(self, text: str) -> List[str]:
        """
        Chunk text by sentence with overlap.
        Uses max_embedding_tokens as the hard limit.

        Args:
            text: Input text (newlines already replaced with spaces)

        Returns:
            List of sentence-based chunks
        """
        if not text.strip():
            return []

        # Split into sentences
        sentences = self._split_sentences(text)

        if not sentences:
            return [text]

        chunks = []
        current_chunk_sentences = []
        current_tokens = 0

        # Use max_embedding_tokens as hard limit to avoid truncation
        max_tokens = self.max_embedding_tokens

        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)

            # If single sentence exceeds embedding limit, split by token
            if sentence_tokens > max_tokens:
                logger.warning(
                    f"Single sentence exceeds embedding limit ({sentence_tokens} > {max_tokens}). "
                    f"Splitting by token."
                )
                # Flush current chunk
                if current_chunk_sentences:
                    chunks.append(" ".join(current_chunk_sentences))
                    current_chunk_sentences = []
                    current_tokens = 0

                # Split long sentence by token
                token_chunks = self._chunk_by_token(sentence)
                chunks.extend(token_chunks)
                continue

            # Check if adding this sentence exceeds limit
            if current_tokens + sentence_tokens > max_tokens:
                # Flush current chunk
                if current_chunk_sentences:
                    chunks.append(" ".join(current_chunk_sentences))

                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(
                    current_chunk_sentences,
                    self.chunk_overlap
                )
                current_chunk_sentences = overlap_sentences + [sentence]
                current_tokens = sum(self.count_tokens(s) for s in current_chunk_sentences)
            else:
                # Add sentence to current chunk
                current_chunk_sentences.append(sentence)
                current_tokens += sentence_tokens

        # Flush remaining chunk
        if current_chunk_sentences:
            chunks.append(" ".join(current_chunk_sentences))

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        if KSS_AVAILABLE:
            # Use kss for Korean sentence splitting
            try:
                sentences = kss.split_sentences(text)
                return [s.strip() for s in sentences if s.strip()]
            except Exception as e:
                logger.warning(f"kss sentence splitting failed: {e}, using fallback")
                return self._split_sentences_fallback(text)
        else:
            return self._split_sentences_fallback(text)

    def _split_sentences_fallback(self, text: str) -> List[str]:
        """
        Fallback sentence splitter (basic).

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        # Simple split by common sentence endings
        import re

        # Split by period, question mark, exclamation followed by space/newline
        sentences = re.split(r'([.!?]\s+)', text)

        # Recombine sentences with their punctuation
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                result.append((sentences[i] + sentences[i + 1]).strip())
            else:
                result.append(sentences[i].strip())

        # Add last sentence if exists
        if len(sentences) % 2 == 1:
            result.append(sentences[-1].strip())

        return [s for s in result if s]

    def _get_overlap_sentences(self, sentences: List[str], overlap_tokens: int) -> List[str]:
        """
        Get sentences for overlap from the end of the list.

        Args:
            sentences: List of sentences
            overlap_tokens: Target overlap in tokens

        Returns:
            List of overlap sentences
        """
        if not sentences or overlap_tokens <= 0:
            return []

        overlap_sentences = []
        total_tokens = 0

        # Take sentences from the end until we reach overlap_tokens
        for sentence in reversed(sentences):
            sentence_tokens = self.count_tokens(sentence)
            if total_tokens + sentence_tokens > overlap_tokens:
                break
            overlap_sentences.insert(0, sentence)
            total_tokens += sentence_tokens

        return overlap_sentences

    def _chunk_by_token(self, text: str) -> List[str]:
        """
        Chunk text by token (fallback for very long sentences).
        Uses max_embedding_tokens as the hard limit.

        Args:
            text: Input text

        Returns:
            List of token-based chunks
        """
        if not text.strip():
            return []

        # Tokenize
        tokens = self.encoding.encode(text)

        # Use max_embedding_tokens as hard limit
        max_tokens = self.max_embedding_tokens

        if len(tokens) <= max_tokens:
            return [text]

        chunks = []
        start = 0

        while start < len(tokens):
            end = start + max_tokens
            chunk_tokens = tokens[start:end]

            # Decode back to text
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)

            # Move start by (max_tokens - overlap)
            start += max_tokens - self.chunk_overlap

        return chunks


# Global instance
text_chunker = TextChunker()
