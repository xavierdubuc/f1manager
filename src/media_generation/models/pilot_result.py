from dataclasses import dataclass, field
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
    visual_config: dict = field(default_factory=dict)

    def get_details_image(self, width: int, height: int, largest_split_width: int, maximum_tyre_amount:int, has_fastest_lap: bool = False, is_pilot_of_the_day:bool = False):
        # [POS] [PILOT] [TYRES] [TIME/SPLIT]
        pilot_config = self.visual_config['pilot']
        split_config = self.visual_config['split']
        pilot_font = FontFactory.get_font(pilot_config.get('font'), pilot_config['font_size'], FontFactory.regular)
        split_font = FontFactory.get_font(split_config.get('font'), split_config['font_size'], FontFactory.regular)
        has_NT_or_DSQ = self.split in ('NT', 'DSQ')

        if is_pilot_of_the_day:
            fg_and_bg_config = self.visual_config['driver_of_the_day']
        elif has_fastest_lap:
            fg_and_bg_config = self.visual_config['fastest_lap']
        elif has_NT_or_DSQ:
            fg_and_bg_config = self.visual_config['nt']
        elif self.position % 4 == 3 or self.position % 4 == 0:
            fg_and_bg_config = self.visual_config['even']
        else:
            fg_and_bg_config = self.visual_config['odd']

        fg_color = fg_and_bg_config['foreground']
        bg_color = fg_and_bg_config['background']

        img = Image.new('RGBA', (width, height), bg_color)
        if is_pilot_of_the_day and has_fastest_lap:
            draw = ImageDraw.Draw(img)
            draw.polygon((
                (width//2, height),
                (width//2+50, 0),
                (width, 0),
                (width, height)
            ), fill=self.visual_config['fastest_lap']['background'], width=3)

        # POSITION
        left_padding = 10
        position_font = FontFactory.get_font(
            self.visual_config['position'].get('font'),
            self.visual_config['position']['font_size'],
            FontFactory.regular
        )
        pos_img = self._get_position_image(font=position_font, color=self.visual_config['position']['font_color'])
        left = left_padding + (height-pos_img.width) // 2
        paste(pos_img, img, left=left, top=self.visual_config['position']['top'])
        pos_right = left_padding + height

        # PILOT
        show_box = not has_fastest_lap and not is_pilot_of_the_day
        pilot_width = width - pos_right
        name_top = self.visual_config['pilot']['top']
        pilot_image = self.pilot.get_ranking_image(
            pilot_width, height, pilot_font, show_box, fg_color, name_top=name_top
        )
        paste(pilot_image, img, left=pos_right+10)

        # SPLIT
        split = self.split if (self.position == 1 or has_NT_or_DSQ) else f'+{self.split}'
        split_img = text(split, fg_color, split_font)
        paste(split_img, img, left=width-split_img.width-20)

        # TYRES
        size_by_tyre = int(.75 * height)
        # we take +1 as a security to avoid any overflow on images
        padding = self._get_tyres_padding(maximum_tyre_amount)+self.visual_config['tyres']['security_on_max_padding']
        max_tyres_size = (maximum_tyre_amount * size_by_tyre) + (maximum_tyre_amount * padding)
        tyres_image = self._get_tyres_image(max_tyres_size, height, size_by_tyre)
        paste(tyres_image, img, left=width - largest_split_width - max_tyres_size)

        return img

    def _get_tyres_image(self, width:int, height:int, size_by_tyre:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        current_left = 0
        padding = self._get_tyres_padding(len(self.tyres))
        for tyre in self.tyres:
            with Image.open(f'./assets/tyres/{tyre}.png') as tyre_img:
                tyre_img = resize(tyre_img, size_by_tyre, size_by_tyre)
            paste(tyre_img, img, left=current_left)
            current_left += (tyre_img.width + padding)
        return img

    def _get_tyres_padding(self, amount_of_tyres:int):
        if amount_of_tyres == 5:
            return self.visual_config['tyres']['padding_5']
        if amount_of_tyres <= 4:
            return self.visual_config['tyres']['padding_4_or_less']
        return self.visual_config['tyres']['padding_more_than_5']

    def _get_position_image(self,
                            font:ImageFont.FreeTypeFont=FontFactory.regular(30),
                            color=(255,255,255)) -> PngImageFile:
        return text(str(self.position), color, font)