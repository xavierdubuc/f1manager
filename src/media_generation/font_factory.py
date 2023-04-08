from PIL import ImageFont
FONT_PATH = 'assets/fonts/'

POLEBG_FONT_NAME = 'Sorren Ex Black.otf'
REGULAR_FONT_NAME = 'Formula1-Regular_web_0.ttf'
BOLD_FONT_NAME = 'Formula1-Bold_web_0.ttf'
WIDE_FONT_NAME = 'Formula1-Wide_web_0.ttf'
BLACK_FONT_NAME = 'Formula1-Black.ttf'

class FontFactory:
    @staticmethod
    def _get_font_path(font_name: str) -> str:
        return f'{FONT_PATH}/{font_name}'

    @staticmethod
    def polebg(size=32, **kwargs) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(FontFactory._get_font_path(POLEBG_FONT_NAME), size, encoding="unic", **kwargs)

    @staticmethod
    def regular(size=32, **kwargs) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(FontFactory._get_font_path(REGULAR_FONT_NAME), size, encoding="unic", **kwargs)

    @staticmethod
    def bold(size=32, **kwargs) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(FontFactory._get_font_path(BOLD_FONT_NAME), size, encoding="unic", **kwargs)

    @staticmethod
    def black(size=32, **kwargs) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(FontFactory._get_font_path(BLACK_FONT_NAME), size, encoding="unic", **kwargs)

    @staticmethod
    def wide(size=32, **kwargs) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(FontFactory._get_font_path(WIDE_FONT_NAME), size, encoding="unic", **kwargs)