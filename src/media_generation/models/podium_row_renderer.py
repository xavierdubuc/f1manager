import logging
from dataclasses import dataclass, field
from PIL import Image, ImageDraw
from src.media_generation.models.ranking_row_renderer import RankingRowRenderer
from src.media_generation.readers.race_reader_models.race_ranking import RaceRankingRow

from ..font_factory import FontFactory
from ..helpers.transform import *


_logger = logging.getLogger(__name__)

@dataclass
class PodiumRowRenderer(RankingRowRenderer):

    def __post_init__(self):
        super().__post_init__()
        self.pilot = self.ranking_row.pilot
        self.team = self.pilot.team
        self.main_bg_color = self.team.standing_bg
        self.main_fg_color = self.team.standing_fg

    def render(self, width:int, height:int) -> PngImageFile:
        img = rounded_rectangle(width, height, self.main_bg_color+(220,))
        position_config = self.visual_config['position']
        position_font = FontFactory.get_font(
            position_config.get('font'),
            position_config['font_size'],
            FontFactory.black
        )
        position_img = text(str(self.ranking_row.position), position_config['color'], position_font)
        paste(position_img, img, left=position_config['left'], top=position_config['top'])

        # PILOT IMG
        face_config = self.visual_config.get('face')
        pilot_img = self.pilot.get_long_range_image()
        pilot_img = resize(pilot_img, height=int(1.25 * height))
        paste(pilot_img, img, top=face_config.get('top', False), left=face_config.get('left', False))

        # DELTA PTS
        deltyrepoints_config = self.visual_config['deltyrepoints']
        deltyrepoints_img = self._render_deltyrepoints(width, deltyrepoints_config['height'])
        deltyrepoints_pos = paste(deltyrepoints_img, img, left=0, top=height-deltyrepoints_img.height)

        # PILOT NAME
        pilot_config = self.visual_config['pilot']
        pilot_img = self._render_pilot(width, pilot_config['height'])
        pilot_pos = paste(pilot_img, img, left=0, top=deltyrepoints_pos.top-pilot_img.height)

        return img

    def _render_deltyrepoints(self, width:int, height:int):
        img = self._render_background(width, height)
        pts_image = self._render_points(height, height)
        paste(pts_image, img, left=width-pts_image.width)

        remaining_width = width-height
        split_image = self._render_split(remaining_width, height//2)
        paste(split_image, img, left=0, top=0)

        # TYRES
        tyres_config = self.visual_config['tyres']
        tyres_images = self._render_tyres(remaining_width, tyres_config['height'])
        paste(tyres_images, img, left=0, top=20)
        return img

    def _render_split(self, width:int, height: int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        split_config = self.visual_config['split']
        if not self.ranking_row.split:
            _logger.warning(f'Missing split for "{self.ranking_row.position}. {self.ranking_row.pilot.name}"')
        
        split_fg = (0,0,0)
        split_font = FontFactory.get_font(split_config.get('font'), split_config['font_size'], FontFactory.regular)
        split_img = text(self.split_str, split_fg, split_font)
        paste(split_img, img)
        return img

    def _render_pilot(self, width:int, height:int):
        pilot = self.ranking_row.pilot
        img = Image.new('RGBA', (width, height), self.main_bg_color)
        pilot_config = self.visual_config['pilot']
        font = FontFactory.get_font(
            pilot_config.get('font'),
            pilot_config['font_size'],
            FontFactory.bold
        )
        pilot_img = text(pilot.name.upper(), self.main_fg_color, font)
        paste(pilot_img, img)
        return img

    def _render_tyres(self, width:int, height: int):
        container = Image.new('RGBA', (width, height), (0,0,0,0))
        tyres_config = self.visual_config['tyres']

        if not self.ranking_row.tyres:
            _logger.warning(f'Missing tyres for "{self.ranking_row.position}. {self.ranking_row.pilot.name}"')

        padding = tyres_config['padding']
        size = int(.5 * height)

        tyre_imgs = []
        for tyre in self.ranking_row.tyres:
            with Image.open(f'./assets/tyres/{tyre}.png') as tyre_img:
                tyre_imgs.append(resize(tyre_img, size, size))

        real_tyre_width = len(tyre_imgs) * size + (len(tyre_imgs) - 1) * padding
        img = Image.new('RGBA', (real_tyre_width, height), (0,0,0,0))
        current_left = 0
        for tyre_img in tyre_imgs:
            paste(tyre_img, img, left=current_left, top=tyres_config['top'])
            current_left += (tyre_img.width + padding)

        paste(img, container)
        return container
