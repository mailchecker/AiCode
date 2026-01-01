"""
PDF Processing V2 - Professional Grade
Span-level text processing with precise positioning and auto-expansion
"""
import fitz  # PyMuPDF
import os
from typing import List, Tuple, Optional, Dict
from ..fonts.font_manager import get_font_manager
from .translator import TextTranslator


class PDFTranslatorV2:
    """Professional PDF translator with span-level precision"""

    def __init__(self, translator: TextTranslator):
        """
        Initialize PDF translator V2

        Args:
            translator: TextTranslator instance
        """
        self.translator = translator
        self.font_manager = get_font_manager()

    def parse_page_range(self, page_range: str, total_pages: int) -> List[int]:
        """
        Parse page range string and return list of page numbers

        Args:
            page_range: "ALL", "3", "1-10" format
            total_pages: Total number of pages

        Returns:
            List of page numbers (0-based index)
        """
        page_range = page_range.strip().upper()

        if page_range == "ALL":
            return list(range(total_pages))

        if "-" in page_range:
            try:
                start, end = page_range.split("-")
                start = int(start.strip()) - 1
                end = int(end.strip()) - 1
                start = max(0, min(start, total_pages - 1))
                end = max(0, min(end, total_pages - 1))
                return list(range(start, end + 1))
            except ValueError:
                raise ValueError(f"Invalid page range format: {page_range}")
        else:
            try:
                page_num = int(page_range) - 1
                if 0 <= page_num < total_pages:
                    return [page_num]
                else:
                    raise ValueError(f"Page number {page_range} out of range (1-{total_pages})")
            except ValueError:
                raise ValueError(f"Invalid page number: {page_range}")

    def translate_pdf(
        self,
        input_path: str,
        output_path: str,
        source_lang: str,
        target_lang: str,
        page_range: str = "ALL",
        progress_callback=None
    ):
        """
        Translate PDF with professional-grade quality

        Args:
            input_path: Input PDF file path
            output_path: Output PDF file path
            source_lang: Source language
            target_lang: Target language
            page_range: Page range ("ALL", "3", "1-10")
            progress_callback: Progress callback function (page_num, total_pages)
        """
        # Open PDF
        doc = fitz.open(input_path)
        total_pages = len(doc)

        # Parse page range
        pages_to_process = self.parse_page_range(page_range, total_pages)

        print(f"Total pages: {total_pages}")
        print(f"Processing pages: {[p+1 for p in pages_to_process]}")

        # Get target language code for font selection
        target_lang_code = self._get_lang_code(target_lang)

        # Process each page
        for page_idx in pages_to_process:
            if progress_callback:
                progress_callback(page_idx + 1, total_pages)

            print(f"\nProcessing page {page_idx + 1}/{total_pages}...")
            page = doc[page_idx]

            # Extract text with detailed structure
            blocks = page.get_text("dict")["blocks"]

            # Filter text blocks
            text_blocks = [b for b in blocks if b["type"] == 0]
            print(f"Found {len(text_blocks)} text blocks on page {page_idx + 1}")

            # Phase 1: Extract and translate all spans
            span_data = self._extract_spans(text_blocks, page_idx)
            print(f"Found {len(span_data)} text spans")

            # Group spans for context-aware translation
            grouped_spans = self._group_spans_for_translation(span_data)
            print(f"Grouped into {len(grouped_spans)} translation units")

            # Phase 2: Translate grouped spans
            translated_spans = self._translate_spans(grouped_spans, source_lang, target_lang)

            # Phase 3: Mark all original text for redaction
            for span in span_data:
                page.add_redact_annot(span['bbox'])

            # Apply redactions
            print(f"[DEBUG] Applying redactions for page {page_idx + 1}")
            page.apply_redactions()

            # Phase 4: Register target language font
            target_font = self.font_manager.get_font_for_language(target_lang_code)
            if target_font:
                try:
                    korean_fontname = "F0"
                    page.insert_font(fontname=korean_fontname, fontbuffer=target_font.buffer)
                    print(f"[DEBUG] Font registered: {korean_fontname}")
                except Exception as e:
                    print(f"[WARNING] Failed to register font: {e}")
                    korean_fontname = None
            else:
                korean_fontname = None
                print(f"[WARNING] No font available for {target_lang_code}")

            # Phase 5: Insert translated text with auto-expansion
            success_count = 0
            for i, (original_span, translated_text) in enumerate(zip(span_data, translated_spans)):
                if self._insert_span_text(
                    page,
                    original_span,
                    translated_text,
                    korean_fontname,
                    page_idx,
                    i
                ):
                    success_count += 1

            print(f"Successfully inserted {success_count}/{len(span_data)} spans")

        # Save
        doc.save(output_path)
        doc.close()

        print(f"\nTranslation complete! Saved to: {output_path}")

    def _get_lang_code(self, language: str) -> str:
        """Convert language name to code"""
        lang_map = {
            'Korean': 'ko',
            'Japanese': 'ja',
            'Chinese': 'zh',
            'Arabic': 'ar',
            'Thai': 'th',
            'English': 'en'
        }
        return lang_map.get(language, 'ko')

    def _extract_spans(self, blocks: list, page_idx: int) -> List[Dict]:
        """
        Extract individual spans with their properties

        Args:
            blocks: Text blocks from page
            page_idx: Page index for debugging

        Returns:
            List of span data dictionaries
        """
        spans = []

        for block_idx, block in enumerate(blocks):
            for line_idx, line in enumerate(block.get("lines", [])):
                for span_idx, span in enumerate(line.get("spans", [])):
                    text = span.get("text", "").strip()

                    if not text:
                        continue

                    # Extract span properties
                    span_data = {
                        'text': text,
                        'bbox': span['bbox'],
                        'font_size': span.get('size', 11),
                        'font_color': span.get('color', 0),
                        'font_flags': span.get('flags', 0),  # Bold, italic, etc.
                        'font_name': span.get('font', 'helv'),
                        'block_idx': block_idx,
                        'line_idx': line_idx,
                        'span_idx': span_idx,
                        # Position for alignment
                        'origin': span.get('origin', (span['bbox'][0], span['bbox'][1]))
                    }

                    spans.append(span_data)

        return spans

    def _group_spans_for_translation(self, spans: List[Dict]) -> List[List[Dict]]:
        """
        Group spans for context-aware translation
        Keep spans on same line together for better translation quality

        Args:
            spans: List of span data

        Returns:
            List of span groups
        """
        if not spans:
            return []

        groups = []
        current_group = [spans[0]]

        for i in range(1, len(spans)):
            prev_span = spans[i-1]
            curr_span = spans[i]

            # Same line if block and line index match
            if (curr_span['block_idx'] == prev_span['block_idx'] and
                curr_span['line_idx'] == prev_span['line_idx']):
                current_group.append(curr_span)
            else:
                # Start new group
                groups.append(current_group)
                current_group = [curr_span]

        # Add last group
        if current_group:
            groups.append(current_group)

        return groups

    def _translate_spans(
        self,
        grouped_spans: List[List[Dict]],
        source_lang: str,
        target_lang: str
    ) -> List[str]:
        """
        Translate grouped spans and distribute to individual spans

        Args:
            grouped_spans: Grouped spans for translation
            source_lang: Source language
            target_lang: Target language

        Returns:
            List of translated texts (one per original span)
        """
        translated_texts = []

        for group in grouped_spans:
            # Combine text from group for translation
            combined_text = " ".join([span['text'] for span in group])

            # Translate
            translated = self.translator.translate(combined_text, source_lang, target_lang)

            # Simple distribution: split by spaces
            # TODO: More intelligent distribution based on original span boundaries
            translated_parts = translated.split()

            # Distribute translated parts to spans
            parts_per_span = max(1, len(translated_parts) // len(group))

            for i, span in enumerate(group):
                start_idx = i * parts_per_span
                end_idx = start_idx + parts_per_span if i < len(group) - 1 else len(translated_parts)

                span_translation = " ".join(translated_parts[start_idx:end_idx])
                translated_texts.append(span_translation if span_translation else translated)

        return translated_texts

    def _insert_span_text(
        self,
        page: fitz.Page,
        span_data: Dict,
        translated_text: str,
        fontname: Optional[str],
        page_idx: int,
        span_idx: int
    ) -> bool:
        """
        Insert translated text for a span with auto-expansion

        Args:
            page: PDF page object
            span_data: Original span data
            translated_text: Translated text
            fontname: Font name to use
            page_idx: Page index for debugging
            span_idx: Span index for debugging

        Returns:
            True if successful, False otherwise
        """
        bbox = span_data['bbox']
        font_size = span_data['font_size']

        # Adjust color (brighten dark colors to black)
        rgb_color = self._int_to_rgb(span_data['font_color'])
        brightness = (rgb_color[0] + rgb_color[1] + rgb_color[2]) / 3
        if brightness > 0.8:
            rgb_color = (0, 0, 0)

        # Try original bbox first
        rc = self._try_insert_text(page, bbox, translated_text, fontname, font_size, rgb_color)

        if rc >= 0:
            return True

        # Try smaller font sizes
        for smaller_size in range(int(font_size) - 1, 3, -1):
            rc = self._try_insert_text(page, bbox, translated_text, fontname, smaller_size, rgb_color)
            if rc >= 0:
                return True

        # Auto-expand bbox (extend downward)
        expanded_bbox = self._expand_bbox(bbox, expansion_ratio=1.5)
        rc = self._try_insert_text(page, expanded_bbox, translated_text, fontname, font_size * 0.8, rgb_color)

        if rc >= 0:
            print(f"[DEBUG] Span {span_idx}: Used expanded bbox")
            return True

        print(f"[WARNING] Failed to insert span {span_idx}: '{translated_text[:30]}...'")
        return False

    def _try_insert_text(
        self,
        page: fitz.Page,
        bbox: Tuple[float, float, float, float],
        text: str,
        fontname: Optional[str],
        fontsize: float,
        color: Tuple[float, float, float]
    ) -> float:
        """
        Try to insert text into bbox

        Returns:
            Result code (negative if failed)
        """
        try:
            if fontname:
                return page.insert_textbox(
                    bbox,
                    text,
                    fontname=fontname,
                    fontsize=fontsize,
                    color=color,
                    align=fitz.TEXT_ALIGN_LEFT
                )
            else:
                return page.insert_textbox(
                    bbox,
                    text,
                    fontname="helv",
                    fontsize=fontsize,
                    color=color,
                    align=fitz.TEXT_ALIGN_LEFT
                )
        except:
            return -1

    def _expand_bbox(
        self,
        bbox: Tuple[float, float, float, float],
        expansion_ratio: float = 1.5
    ) -> Tuple[float, float, float, float]:
        """
        Expand bbox vertically to fit more text

        Args:
            bbox: Original bbox (x0, y0, x1, y1)
            expansion_ratio: How much to expand (1.5 = 50% larger)

        Returns:
            Expanded bbox
        """
        x0, y0, x1, y1 = bbox
        height = y1 - y0
        new_height = height * expansion_ratio

        return (x0, y0, x1, y0 + new_height)

    def _int_to_rgb(self, color_int: int) -> Tuple[float, float, float]:
        """
        Convert integer color to RGB tuple (0-1 range)

        Args:
            color_int: RGB as integer (e.g., 0x000000 for black)

        Returns:
            (r, g, b) tuple with values 0-1
        """
        if color_int == 0:
            return (0, 0, 0)

        r = ((color_int >> 16) & 0xFF) / 255.0
        g = ((color_int >> 8) & 0xFF) / 255.0
        b = (color_int & 0xFF) / 255.0

        return (r, g, b)
