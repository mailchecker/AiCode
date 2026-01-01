"""
Font Manager for PDF Translator
Handles font selection, bundling, and automatic downloading
"""
import os
import platform
import requests
from pathlib import Path
from typing import Optional, Dict
import fitz


class FontManager:
    """Manages fonts for PDF translation with fallback strategies"""

    # Google Fonts download URLs (Noto Sans series)
    GOOGLE_FONTS = {
        'ko': {
            'name': 'NotoSansKR-Regular.ttf',
            'url': 'https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansKR-Regular.otf',
            'display': 'Noto Sans Korean'
        },
        'ja': {
            'name': 'NotoSansJP-Regular.ttf',
            'url': 'https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansJP-Regular.otf',
            'display': 'Noto Sans Japanese'
        },
        'zh': {
            'name': 'NotoSansSC-Regular.ttf',
            'url': 'https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf',
            'display': 'Noto Sans Simplified Chinese'
        },
        'ar': {
            'name': 'NotoSansArabic-Regular.ttf',
            'url': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansArabic/NotoSansArabic-Regular.ttf',
            'display': 'Noto Sans Arabic'
        },
        'th': {
            'name': 'NotoSansThai-Regular.ttf',
            'url': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansThai/NotoSansThai-Regular.ttf',
            'display': 'Noto Sans Thai'
        }
    }

    # System font paths by platform and language
    SYSTEM_FONTS = {
        'Windows': {
            'ko': [
                'C:\\Windows\\Fonts\\malgun.ttf',      # Malgun Gothic
                'C:\\Windows\\Fonts\\gulim.ttc',       # Gulim
                'C:\\Windows\\Fonts\\batang.ttc',      # Batang
            ],
            'ja': [
                'C:\\Windows\\Fonts\\msgothic.ttc',    # MS Gothic
                'C:\\Windows\\Fonts\\msmincho.ttc',    # MS Mincho
            ],
            'zh': [
                'C:\\Windows\\Fonts\\simsun.ttc',      # SimSun
                'C:\\Windows\\Fonts\\msyh.ttc',        # Microsoft YaHei
            ]
        },
        'Darwin': {  # macOS
            'ko': [
                '/System/Library/Fonts/AppleSDGothicNeo.ttc',
                '/Library/Fonts/AppleGothic.ttf',
            ],
            'ja': [
                '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
                '/Library/Fonts/Osaka.ttf',
            ],
            'zh': [
                '/System/Library/Fonts/PingFang.ttc',
                '/Library/Fonts/华文黑体.ttf',
            ]
        },
        'Linux': {
            'ko': [
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            ],
            'ja': [
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf',
            ],
            'zh': [
                '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            ]
        }
    }

    def __init__(self):
        """Initialize font manager"""
        self.fonts_dir = Path(__file__).parent
        self.cache_dir = Path.home() / '.pdf_translator' / 'fonts'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Loaded fonts cache
        self._loaded_fonts: Dict[str, fitz.Font] = {}

    def get_font_for_language(self, lang_code: str, auto_download: bool = True) -> Optional[fitz.Font]:
        """
        Get the best available font for a language

        Args:
            lang_code: Language code ('ko', 'ja', 'zh', etc.)
            auto_download: Whether to automatically download missing fonts

        Returns:
            fitz.Font object or None
        """
        # Check cache
        if lang_code in self._loaded_fonts:
            return self._loaded_fonts[lang_code]

        # Strategy 1: System fonts (fastest)
        system_font = self._find_system_font(lang_code)
        if system_font:
            try:
                font = fitz.Font(fontfile=system_font)
                self._loaded_fonts[lang_code] = font
                print(f"[FontManager] Using system font: {system_font}")
                return font
            except Exception as e:
                print(f"[FontManager] Failed to load system font {system_font}: {e}")

        # Strategy 2: Bundled fonts
        bundled_font = self._find_bundled_font(lang_code)
        if bundled_font:
            try:
                font = fitz.Font(fontfile=bundled_font)
                self._loaded_fonts[lang_code] = font
                print(f"[FontManager] Using bundled font: {bundled_font}")
                return font
            except Exception as e:
                print(f"[FontManager] Failed to load bundled font {bundled_font}: {e}")

        # Strategy 3: Cached downloaded fonts
        cached_font = self._find_cached_font(lang_code)
        if cached_font:
            try:
                font = fitz.Font(fontfile=cached_font)
                self._loaded_fonts[lang_code] = font
                print(f"[FontManager] Using cached font: {cached_font}")
                return font
            except Exception as e:
                print(f"[FontManager] Failed to load cached font {cached_font}: {e}")

        # Strategy 4: Auto-download from Google Fonts
        if auto_download and lang_code in self.GOOGLE_FONTS:
            downloaded_font = self._download_font(lang_code)
            if downloaded_font:
                try:
                    font = fitz.Font(fontfile=downloaded_font)
                    self._loaded_fonts[lang_code] = font
                    print(f"[FontManager] Using downloaded font: {downloaded_font}")
                    return font
                except Exception as e:
                    print(f"[FontManager] Failed to load downloaded font {downloaded_font}: {e}")

        # Fallback: Try to use a generic CJK font
        print(f"[FontManager] WARNING: No suitable font found for {lang_code}")
        return None

    def get_font_path_for_language(self, lang_code: str, auto_download: bool = True) -> Optional[str]:
        """
        Get font file path for a language (for backward compatibility)

        Args:
            lang_code: Language code
            auto_download: Whether to auto-download

        Returns:
            Font file path or None
        """
        # System font
        system_font = self._find_system_font(lang_code)
        if system_font:
            return system_font

        # Bundled font
        bundled_font = self._find_bundled_font(lang_code)
        if bundled_font:
            return bundled_font

        # Cached font
        cached_font = self._find_cached_font(lang_code)
        if cached_font:
            return cached_font

        # Download
        if auto_download:
            return self._download_font(lang_code)

        return None

    def _find_system_font(self, lang_code: str) -> Optional[str]:
        """Find system-installed font"""
        system = platform.system()

        if system not in self.SYSTEM_FONTS:
            return None

        if lang_code not in self.SYSTEM_FONTS[system]:
            return None

        for font_path in self.SYSTEM_FONTS[system][lang_code]:
            if os.path.exists(font_path):
                return font_path

        return None

    def _find_bundled_font(self, lang_code: str) -> Optional[str]:
        """Find bundled font in fonts directory"""
        if lang_code not in self.GOOGLE_FONTS:
            return None

        font_name = self.GOOGLE_FONTS[lang_code]['name']
        bundled_path = self.fonts_dir / font_name

        if bundled_path.exists():
            return str(bundled_path)

        return None

    def _find_cached_font(self, lang_code: str) -> Optional[str]:
        """Find font in cache directory"""
        if lang_code not in self.GOOGLE_FONTS:
            return None

        font_name = self.GOOGLE_FONTS[lang_code]['name']
        cached_path = self.cache_dir / font_name

        if cached_path.exists():
            return str(cached_path)

        return None

    def _download_font(self, lang_code: str) -> Optional[str]:
        """Download font from Google Fonts"""
        if lang_code not in self.GOOGLE_FONTS:
            return None

        font_info = self.GOOGLE_FONTS[lang_code]
        font_name = font_info['name']
        url = font_info['url']
        target_path = self.cache_dir / font_name

        print(f"[FontManager] Downloading {font_info['display']}...")

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            with open(target_path, 'wb') as f:
                f.write(response.content)

            print(f"[FontManager] Downloaded to {target_path}")
            return str(target_path)

        except Exception as e:
            print(f"[FontManager] Download failed: {e}")
            return None

    def preload_fonts(self, lang_codes: list):
        """Preload fonts for multiple languages"""
        for lang_code in lang_codes:
            self.get_font_for_language(lang_code)

    def get_available_languages(self) -> list:
        """Get list of supported language codes"""
        return list(self.GOOGLE_FONTS.keys())


# Global font manager instance
_font_manager = None

def get_font_manager() -> FontManager:
    """Get global font manager instance"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager
