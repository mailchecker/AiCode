# Bundled Fonts

This directory contains bundled fonts for PDF translation.

## Noto Sans Series

All Noto Sans fonts are provided by Google and licensed under the SIL Open Font License (OFL).

### Included Fonts:

- **Noto Sans Korean** - Korean language support
- **Noto Sans Japanese** - Japanese language support
- **Noto Sans Simplified Chinese** - Chinese language support
- **Noto Sans Arabic** - Arabic language support
- **Noto Sans Thai** - Thai language support

### License

SIL Open Font License, Version 1.1

This Font Software is licensed under the SIL Open Font License, Version 1.1.
This license is available with a FAQ at: http://scripts.sil.org/OFL

### Source

Fonts are downloaded from Google's official repositories:
- https://github.com/googlefonts/noto-cjk
- https://github.com/googlefonts/noto-fonts

### Auto-Download

If bundled fonts are not present, the system will automatically download them
from Google Fonts on first use (requires internet connection).

Fonts are cached in: `~/.pdf_translator/fonts/`

## Adding Custom Fonts

To add your own fonts:

1. Place TTF/OTF files in this directory
2. Update `font_manager.py` to include the font path
3. Ensure proper licensing for redistribution
