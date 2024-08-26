from dataclasses import dataclass
from typing import Any, Dict, Tuple

from PIL.PngImagePlugin import PngImageFile
from PIL import Image, ImageDraw


from src.media_generation.helpers.transform import resize
from src.media_generation.layout.layout import Layout


@dataclass
class RoundedLayout(Layout):
    radius: int = 50
    outline: Tuple[int, int, int, int] = None
    thickness: int = 1
    round_top_left: bool = True
    round_top_right: bool = True
    round_bottom_left: bool = True
    round_bottom_right: bool = True

    def _render_base_image(self, context: dict = {}) -> PngImageFile:
        if not self.width or not self.height:
            raise Exception(f'Layout "{self.name}" has no size')
        img = Image.new('RGBA', self.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        round_corners = (
            self._get_round_top_left(context),
            self._get_round_top_right(context),
            self._get_round_bottom_right(context),
            self._get_round_bottom_left(context),
        )
        draw.rounded_rectangle(((0, 0), self.size), radius=self.radius, fill=self._get_bg(context),
                               outline=self.outline, width=self.thickness, corners=round_corners)

        return img

    def _get_round_top_left(self, context: Dict[str, Any] = {}) -> bool:
        return self._get_ctx_attr('round_top_left', context)

    def _get_round_top_right(self, context: Dict[str, Any] = {}) -> bool:
        return self._get_ctx_attr('round_top_right', context)

    def _get_round_bottom_left(self, context: Dict[str, Any] = {}) -> bool:
        return self._get_ctx_attr('round_bottom_left', context)

    def _get_round_bottom_right(self, context: Dict[str, Any] = {}) -> bool:
        return self._get_ctx_attr('round_bottom_right', context)
