from dataclasses import dataclass
from typing import Tuple

from PIL.PngImagePlugin import PngImageFile
from PIL import Image, ImageDraw


from src.media_generation.font_factory import FontFactory
from src.media_generation.helpers.transform import resize
from src.media_generation.layout.layout import Layout

SANDBOX_IMG = Image.new('RGB', (5000, 5000))
SANDBOX = ImageDraw.Draw(SANDBOX_IMG)
DEFAULT_FONT_SIZE = 200
METHOD_FONTS = [
    "polebg", "regular", "bold", "black", "wide"
]


@dataclass
class TextLayout(Layout):
    content: str = None
    font_name: str = "black"
    font_size: int = DEFAULT_FONT_SIZE
    text_left: int = 0
    text_top: int = 0
    stroke_width: int = 0
    stroke_fill: Tuple[int,int,int,int] = None

    @property
    def text_position(self):
        return (self.text_left, self.text_top)

    def __post_init__(self):
        super().__post_init__()
        self.font = self._compute_font()

    def _compute_font(self):
        if self.font_name in METHOD_FONTS:
            return getattr(FontFactory, self.font_name)(self.font_size)
        return FontFactory.get_font(self.font_name, self.font_size)

    def _get_text(self, context: dict = {}) -> str:
        try:
            if not self.content:
                return self.content
            return self.content.format(**context)
        except KeyError as e:
            raise Exception(f"Missing variable \"{e.args[0]}\" in rendering context")

    def _render_base_image(self, context: dict = {}) -> PngImageFile:
        content = self._get_text(context)
        if not content:
            return None
        size = self._estimate_size(content)
        img = Image.new('RGBA', size, self.bg)
        text_draw = ImageDraw.Draw(img)
        text_draw.text(
            self.text_position, content, self.fg, self.font,
            stroke_width=self.stroke_width, stroke_fill=self.stroke_fill
        )
        return resize(img, self.width, self.height)

    def _estimate_size(self, content: str) -> Tuple[int, int]:
        _, _, w, h = SANDBOX.textbbox((0, 0), content, self.font)
        return w+self.text_left,h+self.text_top
