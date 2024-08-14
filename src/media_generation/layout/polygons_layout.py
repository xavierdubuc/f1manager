from dataclasses import dataclass
from typing import List, Tuple

from PIL import ImageDraw
from PIL.PngImagePlugin import PngImageFile

from src.media_generation.layout.layout import Layout


@dataclass
class Polygon:
    edges: Tuple[Tuple[int, int]] = None
    color: Tuple[int, int, int, int] = None


@dataclass
class PolygonsLayout(Layout):
    polygons: List[Polygon] = None

    def __post_init__(self):
        super().__post_init__()
        if self.polygons:
            for p in self.polygons:
                p.color = self._ensure_rgba(p.color)

    def _render_base_image(self, context: dict = {}) -> PngImageFile:
        img = super()._render_base_image(context)
        draw = ImageDraw.Draw(img)
        for p in self.polygons:
            draw.polygon(p.edges, p.color)
        return img
