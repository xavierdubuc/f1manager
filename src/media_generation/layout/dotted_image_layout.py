from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple
from xmlrpc.client import Boolean

from PIL.PngImagePlugin import PngImageFile
from PIL import Image, ImageDraw


from src.media_generation.layout.rounded_layout import RoundedLayout

DARKEN_CONSTANT = 1.1

@dataclass
class DottedImageLayout(RoundedLayout):
    radius: int = 20
    dots_color: Tuple[int, int, int, int] = (189, 189, 189, 255)
    dots_spacing: int = 20
    dots_size: int = 3
    dots_first_left_top: Tuple[int, int] = (20, 14)
    crosses_color: Tuple[int, int, int, int] = (0, 0, 0, 255)
    crosses_positions: List[Tuple[int, int]] = field(default_factory=lambda: [(80, 89), (530, 89)])
    crosses_size: int = 6
    crosses_thickness: int = 2
    left_part_width: int = 84
    left_part_bg: Tuple[int, int, int, int] = None
    round_top_left: bool = False
    round_top_right: bool = False
    round_bottom_left: bool = False
    round_bottom_right: bool = False

    def _compute(self):
        self._ensure_rgba(self.dots_color)
        self._ensure_rgba(self.crosses_color)

    def _render_base_image(self, context: Dict[str, Any] = {}) -> PngImageFile:
        if self.left_part_width > 0:
            img = Image.new('RGBA', self.size, (0, 0, 0, 0))
            self._paste_special_sublayouts(img, context)
        else:
            img = super()._render_base_image(context)
        draw = ImageDraw.Draw(img)
        self._draw_dots(img, draw, context)
        self._draw_crosses(img, draw, context)
        return img

    def _paste_special_sublayouts(self, img: PngImageFile, context: Dict[str, Any] = {}):
        left = RoundedLayout(
            name='left_part',
            height=self.height,
            width=self.left_part_width,
            left=0,
            top=0,
            radius=self.radius,
            outline=self.outline,
            thickness=self.thickness,
            round_top_left=self._get_round_top_left(context),
            round_bottom_left=self._get_round_bottom_left(context),
            round_top_right=False,
            round_bottom_right=False,
            bg=self._get_left_part_bg(context)
        )
        main = RoundedLayout(
            name='main_part',
            width=self.width - self.left_part_width,
            height=self.height,
            top=0,
            left=self.left_part_width,
            radius=self.radius,
            outline=self.outline,
            thickness=self.thickness,
            round_top_left=False,
            round_bottom_left=False,
            round_top_right=self._get_round_top_right(context),
            round_bottom_right=self._get_round_bottom_right(context),
            bg=self._get_bg(context)
        )
        self._paste_child(img, 'left_part', left, context)
        self._paste_child(img, 'main_part', main, context)


    def _get_left_part_bg(self, context: Dict[str, Any] = {}):
        left_part_bg = self._get_ctx_attr('left_part_bg', context, use_format=True)
        if not self.left_part_bg or not left_part_bg:
            bg = self._get_bg(context)
            self.left_part_bg = tuple(int(val/DARKEN_CONSTANT) for i,val in enumerate(bg) if i < 3)
            if len(bg) == 4:
                self.left_part_bg += (bg[3], )

        return self.left_part_bg

    def _draw_crosses(self, img: PngImageFile, draw: ImageDraw.ImageDraw, context: Dict[str, Any] = {}):
        for cross_position in self._get_crosses_positions(context):
            self._draw_cross(img, draw, cross_position)

    def _draw_dots(self, img: PngImageFile, draw: ImageDraw.ImageDraw, context: Dict[str, Any] = {}):
        for left in range(self.dots_first_left_top[0], img.width, self.dots_spacing):
            for top in range(self.dots_first_left_top[1], img.height, self.dots_spacing):
                self._draw_dot(img, draw, (left, top), context)

    def _draw_cross(self, img: PngImageFile, draw: ImageDraw.ImageDraw, position: Tuple[int, int]):
        #  (x, y-(size/2))
        #      |
        #      |
        #  ---------- ((x-(size/2), y), (x+(size/2), y))
        #      |
        #      |
        # (x, y+(size/2))
        size = (self.crosses_size // 2)
        offset = 1 if self.crosses_thickness % 2 == 0 else 0
        lines = [
            # horizontal
            ((position[0] - size, position[1]), (position[0] + size + offset, position[1])),
            # vertical
            ((position[0], position[1] - size), (position[0], position[1] + size + offset)),
        ]
        for line in lines:
            draw.line(line, self.crosses_color, self.crosses_thickness)

    def _draw_dot(self, img: PngImageFile, draw: ImageDraw.ImageDraw, position: Tuple[int, int], context: Dict[str, Any] = {}):
        #  (x, y-(size/2))
        #      |
        #      |
        #  ---------- ((x-(size/2), y), (x+(size/2), y))
        #      |
        #      |
        # (x, y+(size/2))
        dots_color = self._get_dots_color(context)
        for i in range(self.dots_size):
            for j in range(self.dots_size):
                draw.point((position[0]+i, position[1]+j), dots_color)

    def _get_dots_color(self, context: Dict[str, Any] = {}):
        return self._get_ctx_attr('dots_color', context, use_format=True)

    def _get_crosses_positions(self, context: Dict[str, Any] = {}):
        return self._get_ctx_attr('crosses_positions', context)
