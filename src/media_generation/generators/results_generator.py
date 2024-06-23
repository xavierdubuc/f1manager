from typing import List
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
import logging

from src.media_generation.models.podium_row_renderer import PodiumRowRenderer
from src.media_generation.readers.race_reader_models.race_ranking import RaceRankingRow
from src.media_generation.models.visual import Visual
from src.media_generation.generators.abstract_race_generator import AbstractRaceGenerator
from src.media_generation.generators.exceptions import IncorrectDataException
from src.media_generation.models.ranking_row_renderer import RankingRowRenderer
from ..helpers.transform import *

from ..font_factory import FontFactory

DEFAULT_TIME = '-:--.---'

small_font = FontFactory.regular(32)
font = FontFactory.regular(38)
big_font = FontFactory.regular(56)
pilot_font = FontFactory.bold(30)

_logger = logging.getLogger(__name__)


class ResultsGenerator(AbstractRaceGenerator):
    def _get_visual_type(self) -> str:
        return 'results'

    def _generate_part_image(self, config_key):
        config = self.visual_config[config_key]
        method = getattr(self, f'_generate_{config_key}_image')
        return method(config['width'], config['height'])

    def _add_content(self, final: PngImageFile):
        h_padding = self.visual_config['h_padding']
        v_padding = self.visual_config['v_padding']

        # top3
        top3_img = self._generate_part_image('top3')
        top3_pos = paste(top3_img, final, left=h_padding, top=v_padding)

        # top10
        top10_padding = self.visual_config['top10']['padding_top']
        top10_img = self._generate_part_image('top10')
        top10_pos = paste(top10_img, final, left=h_padding, top=top3_pos.bottom+top10_padding)

        # race & fastestlap
        race_flap_padding = self.visual_config['race_flap']['padding_top']
        race_flap_img = self._generate_part_image('race_flap')
        race_flap_pos = paste(race_flap_img, final, left=final.width-race_flap_img.width - h_padding, top=race_flap_padding)

        # top20
        top20_img = self._generate_part_image('top20')
        top20_padding = self.visual_config['top20']['padding_top']
        top20_pos = paste(top20_img, final, left=top3_pos.right+2*h_padding, top=race_flap_pos.bottom+top20_padding)

        # logos
        logo_img = self._generate_part_image('logos')
        logo_padding = self.visual_config['logos']['padding_top']
        paste(logo_img, final, left=top20_pos.left, top=top20_pos.bottom+logo_padding)

    def _generate_top3_image(self, width, height):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        config = self.visual_config['top3']
        renderer_config = self.championship_config['settings']['components']['podium_row_renderer']
        between = 30
        pilot_width = (width - 2 * between) // 3

        pilot_1_renderer = PodiumRowRenderer(self.race.race_result.rows[0], renderer_config)
        pilot_1_img = pilot_1_renderer.render(pilot_width, height)
        pilot_2_renderer = PodiumRowRenderer(self.race.race_result.rows[1], renderer_config)
        pilot_2_img = pilot_2_renderer.render(pilot_width, config['2nd_height'])
        pilot_3_renderer = PodiumRowRenderer(self.race.race_result.rows[2], renderer_config)
        pilot_3_img = pilot_3_renderer.render(pilot_width, config['3rd_height'])

        pilot2_pos = paste(pilot_2_img, img, left=0, top=height-pilot_2_img.height)
        pilot1_pos = paste(pilot_1_img, img, left=pilot2_pos.right+between, top=height-pilot_1_img.height)
        paste(pilot_3_img, img, left=pilot1_pos.right+between, top=height-pilot_3_img.height)

        return img

    def _generate_top10_image(self, width, height):
        return self._generate_pilots_list_image(width, height, self.race.race_result.rows[3:10], 'top10')

    def _generate_top20_image(self, width, height):
        return self._generate_pilots_list_image(width, height, self.race.race_result.rows[10:], 'top20')

    def _generate_race_flap_image(self, width, height):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        flap_config = self.visual_config['race_flap']['fastest_lap']
        race_info_with = width - flap_config['width']
        race_info_img = self._generate_race_info_image(race_info_with, height)
        race_pos = paste(race_info_img, img, left=0)

        flap_img = self.race_renderer.get_fastest_lap_image(flap_config['width']-flap_config['left'], flap_config['height'], flap_config)
        paste(flap_img, img, left=race_pos.right + flap_config['left'])
        return img

    ## SUB - SUB - METHODS

    def _generate_pilots_list_image(self, width:int, height: int, race_rows: List[RaceRankingRow], part:str) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        row_renderer_config = self.championship_config['settings']['components']['ranking_row_renderer']
        top = 0
        row_height = self.visual_config[part]['rows']['height']
        for row in race_rows:
            renderer = RankingRowRenderer(row, row_renderer_config)
            row_img = renderer.render(width, row_height)
            paste(row_img, img, left=0, top=top)
            top += row_height
        return img

    def _generate_race_info_image(self, width:int, height:int):
        img = Image.new('RGB', (width, height), (0,0,0))
        date_config = self.visual_config['race_flap']['date']
        track_config = self.visual_config['race_flap']['track']

        round_img = self.race_renderer.get_type_image(height, height, with_txt=False, round_font=FontFactory.black(32))
        race_img = self.race_renderer.get_circuit_and_date_img(width-round_img.width, height, date_config, track_config)
        round_pos = paste(round_img, img, left=0)
        paste(race_img, img, left=round_pos.right)
        return img

    def _generate_logos_image(self, width, height):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        # champ
        champ_logo = self._get_champ_logo(self.visual_config['logos']['champ'])
        paste(champ_logo, img, left=0)

        # secondary
        champ_logo = self._get_champ_logo(self.visual_config['logos']['secondary'])
        paste(champ_logo, img, left=width - champ_logo.width, top=0)

        # f1
        f1_logo = self._get_f1_logo(self.visual_config['logos']['f1'])
        paste(f1_logo, img, left=width-f1_logo.width, top=height-f1_logo.height)
        return img

    def _get_f1_logo(self, config):
        with Visual.get_f1_logo(config['color']) as f1:
            logo = resize(f1, width=config.get('width'))
        return logo

    def _get_champ_logo(self, config):
        with Image.open(config['path']) as champ:
            logo = resize(champ, width=config.get('width'))
        return logo
