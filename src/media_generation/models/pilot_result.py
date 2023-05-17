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

    def get_details_image(self, width: int, height: int, largest_split_width: int, maximum_tyre_amount:int, has_fastest_lap: bool = False):
        small_font = FontFactory.regular(26)
        pilot_font = FontFactory.regular(30)
        pilot_image = self.pilot.get_ranking_image(
            self.position, width, height, pilot_font, has_fastest_lap)

        split = self.split if (self.position == 1 or self.split in ('NT', 'DSQ')) else f'+{self.split}'
        split_img = text(split, (255,255,255), small_font)
        paste(split_img, pilot_image, left=width-split_img.width-20, use_obj=True)

        max_tyres_size = (maximum_tyre_amount * height) + (maximum_tyre_amount * -12)
        current_left = width - largest_split_width - max_tyres_size
        padding = -12 if len(self.tyres) <= 5 else -28
        for tyre in self.tyres:
            with Image.open(f'./assets/tyres/{tyre}.png') as tyre_img:
                tyre_img.thumbnail((height, height))
                pilot_image.paste(tyre_img, (current_left, 0), tyre_img)
                # tyre_img has a transparent contour
                current_left += (tyre_img.width + padding)

        return pilot_image
