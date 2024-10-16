from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from PIL import ImageDraw
from PIL.PngImagePlugin import PngImageFile

from src.media_generation.layout.layout import Layout


@dataclass
class BicolorLayout(Layout):
    bg_alt: Tuple[int, int, int, int] = None

    def _render_base_image(self, context: dict = {}) -> PngImageFile:
        img = super()._render_base_image(context)
        if bg_alt := self._get_bg_alt(context):
            draw = ImageDraw.Draw(img)
            draw.polygon((
                (self.width//2, self.height),
                (self.width//2+50, 0),
                (self.width, 0),
                (self.width, self.height)
            ), fill=bg_alt, width=3)
        return img

    def _get_bg_alt(self, context: Dict[str, Any] = {}) -> Tuple[int, int, int, int]:
        return self._get_ctx_attr('bg_alt', context, use_format=True)
