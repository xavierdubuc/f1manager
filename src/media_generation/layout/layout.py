import logging
from PIL.PngImagePlugin import PngImageFile
from PIL import Image
from dataclasses import dataclass
from typing import Dict, Tuple

from src.media_generation.helpers.transform import Dimension

_logger = logging.getLogger(__name__)

DEFAULT_OPACITY = 255
DEFAULT_BG = (0, 0, 0, 0)


@dataclass
class Layout:
    # Identifier
    name: str

    # Size
    width: int = None
    height: int = None

    # Pasting information
    left: int = None
    right: int = None
    top: int = None
    bottom: int = None

    # Colors
    bg: Tuple[int, int, int, int] = DEFAULT_BG
    fg: Tuple[int, int, int, int] = (0, 0, 0, DEFAULT_OPACITY)

    # Compositing
    children: Dict[str, "Layout"] = None

    @property
    def size(self):
        return (self.width, self.height)

    def __post_init__(self):
        self.bg = self._ensure_rgba(self.bg)
        self.fg = self._ensure_rgba(self.fg)

    def render(self, context: dict = {}) -> PngImageFile:
        img = self._render_base_image(context)
        if self.children:
            self._paste_children(img, context)
        return img

    def paste_on(self, on: PngImageFile, context: dict = {}) -> Dimension:
        try:
            img = self.render(context)
            if not img:
                return None
            left = self.left
            if left is None and self.right is not None:
                left = on.width - img.width - self.right

            top = self.top
            if top is None and self.bottom is not None:
                top = on.height - img.height - self.bottom

            left = left if left is not None else (on.width-img.width) // 2
            top = top if top is not None else (on.height-img.height) // 2

            if img.mode == 'RGB':
                on.paste(img, (left, top))
            else:
                on.paste(img, (left, top), img)

            return Dimension(left, top, left+img.width, top+img.height)
        except Exception as e:
            raise Exception(f'A problem occured when pasting layout "{self.name}" : {str(e)}') from e

    def _ensure_rgba(self, value):
        if value is None:
            return DEFAULT_BG
        if isinstance(value, int):
            return (value, value, value, DEFAULT_OPACITY)
        if isinstance(value, tuple) and len(value) == 3:
            return value + (DEFAULT_OPACITY, )
        return value

    def _render_base_image(self, context: dict = {}) -> PngImageFile:
        if not self.width or not self.height:
            raise Exception(f'Layout "{self.name}" has no size')
        return Image.new('RGBA', self.size, self.bg)

    def _paste_children(self, img: PngImageFile, context: dict = {}):
        for key, child in self.children.items():
            _logger.debug(f'Pasting {key} on layout {self.__class__.__name__}')
            child.paste_on(img, context)
