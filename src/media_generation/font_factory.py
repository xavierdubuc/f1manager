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
        return FontFactory.font(POLEBG_FONT_NAME, size, ttf=False)

    @staticmethod
    def regular(size=32, **kwargs) -> ImageFont.FreeTypeFont:
        return FontFactory.font(REGULAR_FONT_NAME, size)

    @staticmethod
    def bold(size=32, **kwargs) -> ImageFont.FreeTypeFont:
        return FontFactory.font(BOLD_FONT_NAME, size)

    @staticmethod
    def black(size=32, **kwargs) -> ImageFont.FreeTypeFont:
        return FontFactory.font(BLACK_FONT_NAME, size)

    @staticmethod
    def wide(size=32, **kwargs) -> ImageFont.FreeTypeFont:
        return FontFactory.font(WIDE_FONT_NAME, size)

    @staticmethod
    def font(name:str, size=32, ttf=True, **kwargs) -> ImageFont.FreeTypeFont:
        if ttf:
            name = name if name.endswith('ttf') else f'{name}.ttf'
        return ImageFont.truetype(FontFactory._get_font_path(name), size, encoding="unic", **kwargs)

    @staticmethod
    def get_font(name:str=None, size=32, DefaultFont=None, **kwargs) -> ImageFont.FreeTypeFont:
        if name:
            return FontFactory.font(name, size, **kwargs)
        return DefaultFont(size, **kwargs)