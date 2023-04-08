from dataclasses import dataclass
from PIL import Image, ImageDraw
from .pilot import Pilot
from ..font_factory import FontFactory


@dataclass
class PilotResult:
    pilot: Pilot
    position: int
    split: str
    tyres: str

    def get_details_image(self, width: int, height: int, largest_split_width: int, has_fastest_lap: bool = False, with_fastest_img: bool = True):
        small_font = FontFactory.regular(32)
        pilot_font = FontFactory.bold(30)
        pilot_image = self.pilot.get_ranking_image(
            self.position, width, height, small_font, pilot_font, has_fastest_lap, with_fastest_img)
        draw = ImageDraw.Draw(pilot_image)
        split = self.split if (self.position == 1 or self.split in ('NT', 'DSQ')) else f'+{self.split}'
        _, _, real_split_width, split_height = draw.textbbox((0, 0), split, small_font)
        diff = largest_split_width - real_split_width
        pilot_right = 460

        split_left = pilot_right + diff
        draw.text((split_left, (height-split_height)//2), split, (255, 255, 255), small_font)

        current_left = split_left+real_split_width + 20
        padding = -12 if len(self.tyres) <= 5 else -28
        for tyre in self.tyres:
            with Image.open(f'./assets/tyres/{tyre}.png') as tyre_img:
                tyre_img.thumbnail((height, height))
                pilot_image.paste(tyre_img, (current_left, 0), tyre_img)
                # tyre_img has a transparent contour
                current_left += (tyre_img.width + padding)

        return pilot_image
