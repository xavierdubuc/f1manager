import math
from typing import List
import logging
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.models.pilot import Pilot
from src.media_generation.models.team import Team

from .abstract_generator import AbstractGenerator
from ..helpers.transform import *
from src.media_generation.data import teams_idx as TEAMS

_logger = logging.getLogger(__name__)

class LicensePointsGenerator(AbstractGenerator):
    def __init__(self, championship_config: dict, config: GeneratorConfig, season: int, *args, **kwargs):
        super().__init__(championship_config, config, season, *args, **kwargs)

    def _get_visual_type(self) -> str:
        return 'license_points'

    def _generate_basic_image(self) -> PngImageFile:
        w = self.visual_config['width']
        h = self.visual_config['height']
        bg = Image.new('RGBA', (w,h), self.visual_config['bg_color'])
        with Image.open(self.visual_config['bg_logo']) as logo:
            with Image.open(self.visual_config['bg_logo2']) as logo2:
                logo = resize(logo, height=200)
                logo2 = resize(logo2, height=150)
                paste(logo, bg, top=bg.height-logo.height-50, left=200)
                paste(logo2, bg, top=bg.height-logo2.height-75, left=w-logo2.width-150)
        return bg

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        return None

    def _add_content(self, base_img: PngImageFile):
        title_txt = text('POINTS DE PERMIS', (0,0,0), FontFactory.black(80))
        title_pos = paste(title_txt, base_img, top=self.visual_config['title']['padding_top'])
        subtitle_txt = text(self.config.ranking_subtitle, (0,0,0), FontFactory.regular(60))
        paste(subtitle_txt, base_img, top=title_pos.bottom+self.visual_config['title']['padding_between'])

        pilots_by_points = {}
        top = self.visual_config['body']['top']
        body_height = base_img.height - top
        self.config.ranking.sort_by_license_points()
        for row in self.config.ranking:
            if int(row.amount_of_races) == 0:
                continue
            pilot_name = row.pilot_name
            points = row.license_points
            pilot = self.config.pilots.get(pilot_name)
            if not pilot:
                reservist_team = Team(**self.championship_config['settings']['reservist_team'])
                pilot = Pilot(name=pilot_name, team=reservist_team, number='RE')
            pilots_by_points.setdefault(points, [])
            pilots_by_points[points].append(pilot)

        amount_of_rows = 0
        for points, pilots in pilots_by_points.items():
            amount_of_rows += math.ceil(len(pilots) / self.visual_config['pilots_by_row'])
        row_height = min(int(body_height / amount_of_rows), self.visual_config['body']['max_row_height'])
        padding_h = self.visual_config['body']['padding_h']
        width = base_img.width - padding_h * 2
        for points, pilots in pilots_by_points.items():
            group_img = self._get_group_img(points, pilots, width, row_height)
            pos = paste(group_img, base_img, top=top, left=padding_h)
            top = pos.bottom + self.visual_config['body']['padding_between_rows']

    def _get_group_img(self, points:int, pilots:List[Pilot], width: int, row_height: int):
        amount_of_rows = math.ceil(len(pilots) / self.visual_config['pilots_by_row'])
        inner_row_height = min(row_height, self.visual_config['body']['max_inner_row_height'])
        height = row_height + (amount_of_rows-1) * inner_row_height
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        rectangle = self._get_rectangle_with_points(points, width, height-80)
        top = 0
        left = self.visual_config['rows']['padding_left']
        paste(rectangle, img, top=height-rectangle.height)
        row_pilots = []
        points_width = 150
        row_width = width - points_width - self.visual_config['rows']['padding_left']
        first_row = True
        for (i, pilot) in enumerate(pilots):
            row_pilots.append(pilot)
            if i % self.visual_config['pilots_by_row'] == self.visual_config['pilots_by_row']-1:
                row_img = self._get_pilots_row(row_pilots, row_width, row_height if first_row else inner_row_height)
                first_row = False
                pos = paste(row_img, img, left, top=top)
                top = pos.bottom
                row_pilots = []
        if row_pilots:
            row_img = self._get_pilots_row(row_pilots, row_width, row_height if first_row else inner_row_height)
            pos = paste(row_img, img, left, top=top)
        return img

    def _get_pilots_row(self, pilots:List[Pilot], width:int, height:int):
        img = Image.new('RGBA', (width,height), (0,0,0,0))
        left = 0
        for pilot in pilots:
            pilot_img = pilot.get_close_up_image(height=200)
            pos = paste(pilot_img, img, left=left)
            left = pos.right + self.visual_config['body']['padding_between_pilots']
        names_img = self._get_names_img(pilots, width-left, height)
        paste(names_img, img, left=left)
        return img

    def _get_names_img(self, pilots:List[Pilot], width:int, height:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        bottom = height - 15
        for pilot in reversed(pilots):
            pilot_img = pilot.get_name_image(FontFactory.black(16))
            top = bottom-pilot_img.height
            pos = paste(pilot_img, img, top=top, left=width-pilot_img.width-20)
            bottom = pos.top - 10
        return img

    def _get_rectangle_with_points(self, points:int, width:int, height:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        black_rectangle = rounded_rectangle(width, height, fill=(50,50,50), radius=20)
        paste(black_rectangle, img)

        points_img = text(str(points), (255,255,255), FontFactory.black(120))
        pos = paste(points_img, img,
                top=(height-points_img.height)//2 - 5,
                left=width-points_img.width-self.visual_config['rows']['padding_left'])
        return img