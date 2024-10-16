import logging
from dataclasses import dataclass, field
from typing import List, Tuple

from PIL import ImageDraw
from PIL.PngImagePlugin import PngImageFile
from src.media_generation.layout.layout import Layout

_logger = logging.getLogger(__name__)


@dataclass
class Polygon:
    edges: Tuple[Tuple[int, int]] = None
    color: Tuple[int, int, int, int] = None


DEFAULT_POLYGONS = [
    Polygon(
        edges=(
            (0, 263),
            (0, 510),
            (445, 64),
            (200, 64),
        ),
        color=230
    ),
    Polygon(
        edges=(
            (424, 523),
            (1158, 523),
            (605, 1080),
            (0, 1080),
            (0, 950),
        ),
        color=230
    ),
    Polygon(
        edges=(
            (738, 523),
            (1468, 523),
            (1920, 74),
            (1920, 0),
            (1256, 0),
        ),
        color=230
    ),
    Polygon(
        edges=(
            (1352, 1080),
            (1920, 1080),
            (1920, 523),
            (1908, 523)
        ),
        color=230
    )
]


@dataclass
class PolygonsLayout(Layout):
    polygons: List[Polygon] = field(default_factory=lambda:DEFAULT_POLYGONS)

    def _compute(self):
        super()._compute()
        if self.polygons:
            for p in self.polygons:
                p.color = self._ensure_rgba(p.color)

    def _render_base_image(self, context: dict = {}) -> PngImageFile:
        img = super()._render_base_image(context)
        draw = ImageDraw.Draw(img)
        for p in self.polygons:
            _logger.debug(f"Drawing polygon {p}")
            draw.polygon(p.edges, p.color)
        return img
