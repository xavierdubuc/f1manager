from dataclasses import dataclass
from PIL import Image, ImageDraw
from .pilot import Pilot
from ..font_factory import FontFactory
from ..helpers.transform import *


@dataclass
class PilotResult:
    pilot: Pilot
    position: int
    split: str
    tyres: str

    def get_details_image(self, width: int, height: int, largest_split_width: int, maximum_tyre_amount:int, has_fastest_lap: bool = False, is_pilot_of_the_day:bool = False):
        # [POS] [PILOT] [TYRES] [TIME/SPLIT]
        small_font = FontFactory.regular(26)
        pilot_font = FontFactory.regular(30)
        has_NT_or_DSQ = self.split in ('NT', 'DSQ')

        fg_color = (255,255,255)
        if is_pilot_of_the_day:
            bg_color = (190, 140, 20)
        elif has_fastest_lap:
            bg_color = (160, 25, 190, 255)
        elif has_NT_or_DSQ:
            fg_color = (150,150,150)
            bg_color = (75, 75, 75, 235)
        # elif self.position % 4 == 3 or self.position % 4 == 0:
        #     bg_color = (50, 50, 50, 235) # COULD BE NICE WHEN ALL ROWS ARE SAME HEIGHT
        else:
            bg_color = (30, 30, 30, 235)

        img = Image.new('RGBA', (width, height), bg_color)

        # POSITION
        left_padding = 10
        pos_img = self._get_position_image(color=fg_color)
        left = left_padding + (height-pos_img.width) // 2
        paste(pos_img, img, left=left)
        pos_right = left_padding + height

        # PILOT
        show_box = not has_fastest_lap and not is_pilot_of_the_day
        pilot_width = width - pos_right
        pilot_image = self.pilot.get_ranking_image(
            pilot_width, height, pilot_font, show_box, fg_color
        )
        paste(pilot_image, img, left=pos_right+10, use_obj=True)

        # SPLIT
        split = self.split if (self.position == 1 or has_NT_or_DSQ) else f'+{self.split}'
        split_img = text(split, fg_color, small_font)
        paste(split_img, img, left=width-split_img.width-20, use_obj=True)

        # TYRES
        max_tyres_size = (maximum_tyre_amount * height) + (maximum_tyre_amount * -12)
        tyres_image = self._get_tyres_image(max_tyres_size, height)
        paste(tyres_image, img, left=width - largest_split_width - max_tyres_size)

        return img

    def _get_tyres_image(self, width:int, height:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        current_left = 0
        padding = -12 if len(self.tyres) <= 5 else -28
        for tyre in self.tyres:
            with Image.open(f'./assets/tyres/{tyre}.png') as tyre_img:
                tyre_img = resize(tyre_img, height, height)
            paste(tyre_img, img, left=current_left)
            # tyre_img has a transparent contour
            current_left += (tyre_img.width + padding)
        return img

    def _get_position_image(self,
                            font:ImageFont.FreeTypeFont=FontFactory.regular(30),
                            color=(255,255,255)) -> PngImageFile:
        return text(str(self.position), color, font)