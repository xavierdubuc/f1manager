from dataclasses import dataclass
from typing import Any, Dict

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.image_layout import ImageLayout
from src.media_generation.layout.layout import Layout
from src.media_generation.layout.rounded_layout import RoundedLayout
from src.media_generation.layout.text_layout import TextLayout


@dataclass
class ProgressionLayout(RoundedLayout):
    value: int = None
    text_height: int = None
    text_width: int = None
    text_top: int = None
    text_left: int = None
    text_only_top: int = None
    text_only_left: int = None
    image_height: int = None
    image_width: int = None
    image_top: int = None
    image_left: int = None

    def _get_value(self, context: Dict[str, Any] = {}) -> int:
        return self._get_ctx_attr('value', context) or 0

    def _render_base_image(self, context: Dict[str, Any] = {}) -> PngImageFile:
        img = super()._render_base_image(context)
        value = self._get_value(context)
        if value == 0:
            self._paste_child(img, "no_evolution", self._get_no_move_layout(context))
        else:
            self._paste_child(img, "evolution", self._get_evolution_layout(context))

        return img

    def _get_evolution_layout(self, context: Dict[str, Any] = {}) -> TextLayout:
        value = self._get_value(context)
        return Layout(
            height=self.height,
            width=self.width,
            name="evolution",
            children={
                "evolution_txt": TextLayout(
                    name="evolution_txt",
                    height=self.text_height,
                    width=self.text_width,
                    left=self.text_left,
                    top=self.text_top,
                    content=str(abs(value))
                ),
                "evolution_img": ImageLayout(
                    name="evolution_img",
                    height=self.image_height,
                    width=self.image_width,
                    left=self.image_left,
                    top=self.image_top,
                    path="assets/up.png" if value > 0 else "assets/down.png"
                )
            })

    def _get_no_move_layout(self, context: Dict[str, Any] = {}) -> TextLayout:
        return TextLayout(
            name="no_evolution",
            height=self.text_height,
            width=self.text_width,
            left=self.text_only_left,
            top=self.text_only_top,
            content="-"
        )
