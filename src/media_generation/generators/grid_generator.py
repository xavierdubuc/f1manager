import logging
from PIL import Image, ImageFilter

from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.readers.general_ranking_models.pilot_ranking import PilotRanking
from src.media_generation.generators.abstract_race_generator import AbstractRaceGenerator
from src.media_generation.readers.race_reader_models.race_ranking import RaceRankingRow

from ..helpers.transform import *
from ..font_factory import FontFactory
from ..models import Pilot, Team, Visual

_logger = logging.getLogger(__name__)


class GridGenerator(AbstractRaceGenerator):
    def _get_visual_type(self) -> str:
        return 'grid'

    def _get_background_image(self) -> PngImageFile:
        bg = super()._get_background_image()
        if not bg:
            return bg
        return bg.filter(ImageFilter.GaussianBlur(5))

    def _add_content(self, final: PngImageFile):
        right_content_width = self.visual_config.get('right_content_width', 1585)
        right_content_img = self._get_right_content(right_content_width, final.height)
        right_content_left = self.visual_config.get('right_content', {}).get('left', 270)
        paste(right_content_img, final, right_content_left, 0)

        self._render_logos(final)
        self._render_circuit(final)
        self._render_round(final)
        self._render_thegrid_title(final)

    def _render_circuit(self, base_img:PngImageFile):
        config = self.visual_config.get('circuit', {})
        flag_config = config.get('flag', {})
        flag_w = flag_config.get('width', 100)
        flag_h = flag_config.get('height', 100)
        with self.race.circuit.get_flag() as flag_img:
            flag_img = resize(flag_img, flag_w, flag_h)
        self.paste_image(flag_img, base_img, flag_config)

        name_config = config.get('name', {})
        name_content = f'{self.race.circuit.city}'.upper()
        name_img = text_hi_res(
            name_content, name_config.get('color', (255,255,255)),
            FontFactory.regular(40),
            name_config.get('width', 500), name_config.get('height', 40),
        )
        self.paste_image(name_img, base_img, name_config)

    def _render_logos(self, base_img: PngImageFile):
        logo_configs = self.visual_config.get('logos', [])
        if not logo_configs:
            return
        for logo_config in logo_configs:
            self.paste_image_from_config(logo_config, base_img)

    def _render_round(self, base_img: PngImageFile):
        round_config = self.visual_config.get('round', {})
        round_img = self.race_renderer.get_race_type_image(round_config)
        self.paste_image(round_img, base_img, round_config)

    def _render_thegrid_title(self, base_img: PngImageFile):
        # THE GRID title
        config = self.visual_config.get('the_grid', {})
        w = config.get('width')
        h = config.get('width')
        bg = config.get('background', (0,0,0,255))
        font = FontFactory.get_font(
            config.get('font_name'), 50, FontFactory.black
        )
        the_grid_color = config.get('font_color', (255, 255, 255))
        the_img = text_hi_res('THE', the_grid_color, font, w, h, use_background=bg)
        grid_img = text_hi_res('GRID', the_grid_color, font, w, h, use_background=bg)
        self.paste_image(the_img, base_img, config.get("the", {}))
        self.paste_image(grid_img, base_img, config.get("grid", {}))

    def _get_right_content(self, width: int, height: int) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        content_config = self.visual_config['right_content']
        rows_config = content_config['rows']

        padding_between_cols = content_config.get('padding_between_cols', 43)
        padding_between_rows = content_config.get('padding_between_rows', 43)
        position_height = rows_config.get('', 65)
        position_width = (width - padding_between_cols) // 2
        left_column_left = 0
        right_column_left = left_column_left + position_width + padding_between_cols
        initial_left_top = content_config.get('padding_top', 50)
        initial_right_top = content_config.get('padding_top', 89)

        last_left_pos = last_right_pos = None
        for result in self.race.qualification_result.rows:
            result_img = self._get_result_img(position_width, position_height, result)
            if result.position % 2 == 1:
                top = (last_left_pos.bottom + padding_between_rows) if last_left_pos else initial_left_top
                last_left_pos = paste(result_img, img, left_column_left, top)
            else:
                top = (last_right_pos.bottom + padding_between_rows) if last_right_pos else initial_right_top
                last_right_pos = paste(result_img, img, right_column_left, top)

        return img

    def _get_result_img(self, width:int, height:int, result:RaceRankingRow):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        rows_config = self.visual_config['right_content'].get('rows', {})
        pos_config = rows_config.get('position', {})
        pos_bg = pos_config.get("background", (255, 255, 255))
        
        pos_img = Image.new('RGB', (pos_config.get('width', 156), height), pos_bg)
        font = FontFactory.get_font(pos_config.get('font_name'), pos_config.get('font_size', 30),
                                    FontFactory.black)
        font_color = pos_config.get('font_color', (255,255,255))
        pos_txt = text(str(result.position), font_color, font)
        paste(pos_txt, pos_img)
        position_pos = paste(pos_img, img, left = 0)

        # TEAM
        pilot = result.pilot
        if not pilot:
            raise Exception(f'{result.pilot_name} not found on qualification results !')
        team_card_img = pilot.team.build_card_image(width - pos_img.width, height)
        team_name_pos = paste(team_card_img, img, left=position_pos.right,)

        # pilot name
        pilot_config = rows_config.get('pilot', {})

        pilot_font = FontFactory.get_font(pilot_config.get('font_name'), pilot_config.get('font_size', 30),
                                    FontFactory.black)

        team_txt = text(pilot.name.upper(), pilot.team.standing_fg, pilot_font)
        paste(team_txt, img, team_name_pos.left+pilot_config.get('left_padding', 200))
        return img
