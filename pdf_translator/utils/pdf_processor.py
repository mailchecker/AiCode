"""
PDF Processing with PyMuPDF (fitz)
Extracts text while preserving layout, translates, and replaces text
"""
import fitz  # PyMuPDF
import os
import platform
from typing import List, Tuple, Optional
from .translator import TextTranslator


class PDFTranslator:
    """PDF 문서의 텍스트를 번역하면서 레이아웃을 유지하는 클래스"""

    def __init__(self, translator: TextTranslator):
        """
        Initialize PDF translator

        Args:
            translator: TextTranslator 인스턴스
        """
        self.translator = translator
        self.korean_font_path = self._get_korean_font()

    def _get_korean_font(self) -> Optional[str]:
        """
        시스템에서 한글 폰트 찾기

        Returns:
            한글 폰트 파일 경로 또는 None
        """
        system = platform.system()

        # Windows 폰트 경로
        if system == "Windows":
            font_paths = [
                "C:\\Windows\\Fonts\\malgun.ttf",      # 맑은 고딕
                "C:\\Windows\\Fonts\\gulim.ttc",       # 굴림
                "C:\\Windows\\Fonts\\batang.ttc",      # 바탕
                "C:\\Windows\\Fonts\\NanumGothic.ttf", # 나눔고딕
            ]
        # macOS 폰트 경로
        elif system == "Darwin":
            font_paths = [
                "/System/Library/Fonts/AppleSDGothicNeo.ttc",
                "/Library/Fonts/AppleGothic.ttf",
            ]
        # Linux 폰트 경로
        else:
            font_paths = [
                "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            ]

        # 존재하는 첫 번째 폰트 반환
        for font_path in font_paths:
            if os.path.exists(font_path):
                print(f"Using Korean font: {font_path}")
                return font_path

        print("Warning: No Korean font found, text may not display correctly")
        return None

    def parse_page_range(self, page_range: str, total_pages: int) -> List[int]:
        """
        Parse page range string and return list of page numbers

        Args:
            page_range: "ALL", "3", "1-10" 형식의 문자열
            total_pages: 전체 페이지 수

        Returns:
            처리할 페이지 번호 리스트 (0-based index)
        """
        page_range = page_range.strip().upper()

        if page_range == "ALL":
            return list(range(total_pages))

        if "-" in page_range:
            # 범위 지정 (예: "1-10")
            try:
                start, end = page_range.split("-")
                start = int(start.strip()) - 1  # 1-based to 0-based
                end = int(end.strip()) - 1
                start = max(0, min(start, total_pages - 1))
                end = max(0, min(end, total_pages - 1))
                return list(range(start, end + 1))
            except ValueError:
                raise ValueError(f"Invalid page range format: {page_range}")
        else:
            # 특정 페이지 (예: "3")
            try:
                page_num = int(page_range) - 1  # 1-based to 0-based
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
        Translate PDF while preserving layout

        Args:
            input_path: 입력 PDF 파일 경로
            output_path: 출력 PDF 파일 경로
            source_lang: 원본 언어
            target_lang: 대상 언어
            page_range: 페이지 범위 ("ALL", "3", "1-10")
            progress_callback: 진행 상황 콜백 함수 (page_num, total_pages)
        """
        # PDF 열기
        doc = fitz.open(input_path)
        total_pages = len(doc)

        # 페이지 범위 파싱
        pages_to_process = self.parse_page_range(page_range, total_pages)

        print(f"Total pages: {total_pages}")
        print(f"Processing pages: {[p+1 for p in pages_to_process]}")

        # 각 페이지 처리
        for page_idx in pages_to_process:
            if progress_callback:
                progress_callback(page_idx + 1, total_pages)

            print(f"\nProcessing page {page_idx + 1}/{total_pages}...")
            page = doc[page_idx]

            # 페이지에 한글 폰트 등록
            korean_fontname = None
            if self.korean_font_path:
                try:
                    korean_fontname = page.insert_font(fontfile=self.korean_font_path)
                    print(f"Korean font registered on page: {korean_fontname}")
                except Exception as e:
                    print(f"Failed to register Korean font on page: {e}")
                    korean_fontname = None

            # 텍스트 블록 추출 (위치 정보 포함)
            blocks = page.get_text("dict")["blocks"]

            # 텍스트 블록만 필터링 (이미지는 제외)
            text_blocks = [b for b in blocks if b["type"] == 0]

            print(f"Found {len(text_blocks)} text blocks on page {page_idx + 1}")

            # 각 텍스트 블록 처리
            for block_idx, block in enumerate(text_blocks):
                try:
                    # 블록 내의 모든 텍스트 추출
                    block_text = ""
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            block_text += span.get("text", "")
                        block_text += "\n"

                    block_text = block_text.strip()

                    if not block_text:
                        continue

                    # 텍스트 번역
                    translated_text = self.translator.translate(
                        block_text,
                        source_lang,
                        target_lang
                    )

                    # 원본 텍스트 영역 정보
                    bbox = block["bbox"]  # (x0, y0, x1, y1)

                    # 첫 번째 span의 폰트 정보 가져오기
                    first_span = block["lines"][0]["spans"][0] if block.get("lines") and block["lines"][0].get("spans") else None

                    # 폰트 크기와 색상 정보
                    if first_span:
                        font_size = first_span.get("size", 11)
                        font_color = first_span.get("color", 0)  # RGB as integer
                    else:
                        font_size = 11
                        font_color = 0

                    # 원본 텍스트 영역에 흰색 사각형 그리기 (텍스트 지우기)
                    page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1))

                    # 번역된 텍스트 삽입 (한글 폰트 사용)
                    # 텍스트가 영역에 맞도록 자동 조정
                    try:
                        if korean_fontname:
                            # 등록된 한글 폰트 이름 사용
                            rc = page.insert_textbox(
                                bbox,
                                translated_text,
                                fontname=korean_fontname,
                                fontsize=font_size,
                                color=self._int_to_rgb(font_color),
                                align=fitz.TEXT_ALIGN_LEFT
                            )
                        else:
                            # 폰트가 없으면 기본 폰트 사용 (영어만 가능)
                            rc = page.insert_textbox(
                                bbox,
                                translated_text,
                                fontname="helv",
                                fontsize=font_size,
                                color=self._int_to_rgb(font_color),
                                align=fitz.TEXT_ALIGN_LEFT
                            )
                    except Exception as font_error:
                        print(f"Font error, using fallback: {font_error}")
                        # Fallback: 기본 설정으로 재시도
                        try:
                            if korean_fontname:
                                rc = page.insert_textbox(
                                    bbox,
                                    translated_text,
                                    fontname=korean_fontname,
                                    fontsize=11,
                                    color=(0, 0, 0),
                                    align=fitz.TEXT_ALIGN_LEFT
                                )
                            else:
                                rc = page.insert_textbox(
                                    bbox,
                                    translated_text,
                                    fontname="helv",
                                    fontsize=11,
                                    color=(0, 0, 0),
                                    align=fitz.TEXT_ALIGN_LEFT
                                )
                        except:
                            rc = -1  # 실패

                    # 텍스트가 영역을 초과하면 폰트 크기 줄이기
                    if rc < 0:
                        # 폰트 크기를 줄여가며 재시도
                        for smaller_size in range(int(font_size) - 1, 6, -1):
                            page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1))
                            try:
                                if korean_fontname:
                                    rc = page.insert_textbox(
                                        bbox,
                                        translated_text,
                                        fontname=korean_fontname,
                                        fontsize=smaller_size,
                                        color=self._int_to_rgb(font_color),
                                        align=fitz.TEXT_ALIGN_LEFT
                                    )
                                else:
                                    rc = page.insert_textbox(
                                        bbox,
                                        translated_text,
                                        fontname="helv",
                                        fontsize=smaller_size,
                                        color=self._int_to_rgb(font_color),
                                        align=fitz.TEXT_ALIGN_LEFT
                                    )
                            except:
                                # 최후의 수단: 최소한의 설정으로 시도
                                try:
                                    if korean_fontname:
                                        rc = page.insert_textbox(
                                            bbox,
                                            translated_text,
                                            fontname=korean_fontname,
                                            fontsize=smaller_size,
                                            color=(0, 0, 0),
                                            align=fitz.TEXT_ALIGN_LEFT
                                        )
                                    else:
                                        rc = page.insert_textbox(
                                            bbox,
                                            translated_text,
                                            fontname="helv",
                                            fontsize=smaller_size,
                                            color=(0, 0, 0),
                                            align=fitz.TEXT_ALIGN_LEFT
                                        )
                                except:
                                    pass
                            if rc >= 0:
                                break

                except Exception as e:
                    print(f"Error processing block {block_idx} on page {page_idx + 1}: {e}")
                    continue

        # 저장
        doc.save(output_path)
        doc.close()

        print(f"\nTranslation complete! Saved to: {output_path}")

    def _int_to_rgb(self, color_int: int) -> Tuple[float, float, float]:
        """
        Convert integer color to RGB tuple (0-1 range)

        Args:
            color_int: RGB as integer (e.g., 0x000000 for black)

        Returns:
            (r, g, b) tuple with values 0-1
        """
        if color_int == 0:
            return (0, 0, 0)  # Black

        r = ((color_int >> 16) & 0xFF) / 255.0
        g = ((color_int >> 8) & 0xFF) / 255.0
        b = (color_int & 0xFF) / 255.0

        return (r, g, b)
