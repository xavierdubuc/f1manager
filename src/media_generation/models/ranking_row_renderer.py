import logging
from dataclasses import dataclass, field
from PIL import Image, ImageDraw
from src.media_generation.readers.race_reader_models.race_ranking import RaceRankingRow

from ..font_factory import FontFactory
from ..helpers.transform import *


_logger = logging.getLogger(__name__)

@dataclass
class RankingRowRenderer:
    ranking_row: RaceRankingRow
    visual_config: dict = field(default_factory=dict)

    def __post_init__(self):
        self.has_NT_or_DSQ = self.ranking_row.split in ('NT', 'DSQ')
        fg_and_bg_config = self._get_fg_and_bg_config()
        self.fg_color = fg_and_bg_config['foreground']
        self.bg_color = fg_and_bg_config['background']
        if self.ranking_row.position == 1 or self.has_NT_or_DSQ or not self.ranking_row.split:
            self.split_str = self.ranking_row.split
        else:
            self.split_str = f'+{self.ranking_row.split}'

    def get_details_image(self, width: int, height: int, largest_split_width: int, maximum_tyre_amount:int):
        # [POS] [PILOT] [TYRES] [TIME/SPLIT]
        pilot_config = self.visual_config['pilot']
        split_config = self.visual_config['split']
        position_config = self.visual_config['position']

        pilot_font = FontFactory.get_font(pilot_config.get('font'), pilot_config['font_size'], FontFactory.regular)
        split_font = FontFactory.get_font(split_config.get('font'), split_config['font_size'], FontFactory.regular)

        img = Image.new('RGBA', (width, height), self.bg_color)
        if self.ranking_row.is_driver_of_the_day and self.ranking_row.has_fastest_lap:
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
            position_config.get('font'),
            position_config['font_size'],
            FontFactory.regular
        )
        pos_img = self._get_position_image(font=position_font, color=position_config['font_color'])
        left = left_padding + (height-pos_img.width) // 2
        paste(pos_img, img, left=left, top=position_config['top'])
        pos_right = left_padding + height

        # PILOT
        show_box = not self.ranking_row.has_fastest_lap and not self.ranking_row.is_driver_of_the_day
        pilot_width = width - pos_right
        name_top = self.visual_config['pilot']['top']
        pilot_image = self.ranking_row.pilot.get_ranking_image(
            pilot_width, height, pilot_font, show_box, self.fg_color, name_top=name_top
        )
        paste(pilot_image, img, left=pos_right+10)

        # SPLIT
        if not self.ranking_row.split:
            _logger.warning(f'Missing split for "{self.ranking_row.position}. {self.ranking_row.pilot.name}"')
        split_img = text(self.split_str, self.fg_color, split_font)
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
        padding = self._get_tyres_padding(len(self.ranking_row.tyres))
        if not self.ranking_row.tyres:
            _logger.warning(f'Missing tyres for "{self.ranking_row.position}. {self.ranking_row.pilot.name}"')
        for tyre in self.ranking_row.tyres:
            with Image.open(f'./assets/tyres/{tyre}.png') as tyre_img:
                tyre_img = resize(tyre_img, size_by_tyre, size_by_tyre)
            paste(tyre_img, img, left=current_left)
            current_left += (tyre_img.width + padding)
        return img

    def _get_tyres_padding(self, amount_of_tyres:int):
        key = 'padding_more_than_5'
        if amount_of_tyres == 5:
            key = 'padding_5'
        elif amount_of_tyres <= 4:
            key = 'padding_4_or_less'
        return self.visual_config['tyres'][key]

    def _get_position_image(self,
                            font:ImageFont.FreeTypeFont=FontFactory.regular(30),
                            color=(255,255,255)) -> PngImageFile:
        return text(str(self.ranking_row.position), color, font)

    def _get_fg_and_bg_config(self):
        if self.ranking_row.is_driver_of_the_day:
            key = 'driver_of_the_day'
        elif self.ranking_row.has_fastest_lap:
            key ='fastest_lap'
        elif self.has_NT_or_DSQ:
            key = 'nt'
        elif self.ranking_row.position % 4 == 3 or self.ranking_row.position % 4 == 0:
            key = 'even'
        else:
            key = 'odd'
        return self.visual_config[key]
