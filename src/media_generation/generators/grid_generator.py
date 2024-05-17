import logging
from PIL import Image

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

    def _add_content(self, final: PngImageFile):
        left_content_width = self.visual_config.get('left_content_width', 250)
        padding_left = self.visual_config.get('padding_left', 20)
        padding_between = self.visual_config.get('padding_between_left_and_right_content', 20)
        left_content_img = self._get_left_content(left_content_width, final.height)
        left_content_pos = paste(left_content_img, final, padding_left, 0)

        right_content_width = self.visual_config.get('right_content_width', 1585)
        right_content_img = self._get_right_content(right_content_width, final.height)
        right_content_pos = paste(right_content_img, final, left_content_pos.right+padding_between, 0)

    def _get_left_content(self, width: int, height: int) -> PngImageFile:
        content_config = self.visual_config['left_content']
        default_padding = 20
        img = Image.new('RGBA', (width, height), (0,0,0,0))

        # FBRT
        fbrt_logo_size = int(0.8 * width)
        fbrt_logo = resize(Visual.get_fbrt_round_logo(), fbrt_logo_size)
        fbrt_logo_pos = paste(fbrt_logo, img, top=20)

        # F1
        f1_logo_size = width
        with Visual.get_f1_logo('black') as f1_logo_img:
            f1_logo_img = resize(f1_logo_img, f1_logo_size, f1_logo_size)
            f1_logo_pos = paste(f1_logo_img, img, top=img.height - f1_logo_img.height - 40)

        # FIF
        fif_logo_size = width
        with Visual.get_fif_logo('wide') as fif_logo_img:
            fif_logo_img = resize(fif_logo_img, fif_logo_size, fif_logo_size)
            fif_logo_pos = paste(fif_logo_img, img, top=f1_logo_pos.top - fif_logo_img.height)

        # R
        round_config = content_config.get('round', {})
        round_size = int(0.5 * width)
        round = self.race_renderer.get_type_image(round_size, round_size)
        round_pos = paste(round, img, top = fbrt_logo_pos.bottom + round_config.get('padding_top', default_padding))

        # THE GRID title
        the_grid_config = content_config.get('the_grid', {})
        the_grid_font = FontFactory.get_font(the_grid_config.get('font_name'),
                                             the_grid_config.get('font_size', 60),
                                             FontFactory.black)
        the_grid_color = the_grid_config.get('font_color', (0,0,0))
        padding_between_round_and_title = the_grid_config.get('padding_top', default_padding)
        the_img = text('THE', the_grid_color, the_grid_font)
        the_pos = paste(the_img, img, top=round_pos.bottom + padding_between_round_and_title)
        grid_img = text('GRID', the_grid_color, the_grid_font)
        grid_pos = paste(grid_img, img, top=the_pos.bottom+5)

        # FLAG
        flag_config = content_config.get('flag', {})
        with self.race.circuit.get_flag() as flag:
            flag = resize(flag, int(0.8*width))
            flag_pos = paste(flag, img,top= grid_pos.bottom + flag_config.get('padding_top', default_padding))

        # CIRCUIT NAME
        circuit_name_config = content_config.get('circuit_name', {})
        circuit_name_font = FontFactory.get_font(circuit_name_config.get('font_name'),
                                             circuit_name_config.get('font_size', 34),
                                             FontFactory.black)
        circuit_name_color = circuit_name_config.get('font_color', (230,0,0))
        circuit_name_img = self.race.circuit.get_name_img(circuit_name_font, circuit_name_color)
        circuit_name_ptop = circuit_name_config.get('padding_top', default_padding)

        # CIRCUIT CITY
        circuit_city_config = content_config.get('circuit_city', {})
        circuit_city_font = FontFactory.get_font(circuit_city_config.get('font_name'),
                                             circuit_city_config.get('font_size', 28),
                                             FontFactory.black)
        circuit_city_color = circuit_city_config.get('font_color', (255, 255, 255))
        circuit_city_img = self.race.circuit.get_city_img(circuit_city_font, circuit_city_color)
        circuit_city_ptop = circuit_city_config.get('padding_top', 5)

        # RACE DATE
        date_txt = f'{self.race.day} {date_fr(self.race.month).upper()}'
        date_config = content_config.get('date', {})
        date_font = FontFactory.get_font(date_config.get('font_name'),
                                         date_config.get('font_size', 30),
                                         FontFactory.regular)
        date_color = date_config.get('font_color', (255, 255, 255))
        date_img = text(date_txt, date_color, date_font)
        date_ptop = date_config.get('padding_top', 20)
        date_pbot = date_config.get('padding_bottom', 20)

        # --- BLACK BG
        black_bg_config = content_config.get('black_bg', {})
        black_bg_height = sum((
            circuit_name_ptop,
            circuit_name_img.height,
            circuit_city_ptop,
            circuit_city_img.height,
            date_ptop,
            date_img.height,
            date_pbot,
        ))
        black_bg = Image.new('RGB', (width, black_bg_height), (0,0,0))
        black_bg_pos = paste(black_bg, img, left=0, top=flag_pos.bottom + black_bg_config.get('padding_top', 20))

        circuit_name_pos = paste(circuit_name_img, img, top=black_bg_pos.top+circuit_name_ptop)
        circuit_city_pos = paste(circuit_city_img, img, top=circuit_name_pos.bottom+circuit_city_ptop)
        circuit_date_pos = paste(date_img, img, top=circuit_city_pos.bottom+date_ptop)

        return img

    def _get_right_content(self, width: int, height: int) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        content_config = self.visual_config['right_content']
        rows_config = content_config['rows']

        padding_between_cols = content_config.get('padding_between_cols', 43)
        padding_between_rows = content_config.get('padding_between_rows', 43)
        position_height = rows_config.get('', 65)
        position_width = (width - padding_between_cols) // 2
        starting_grid_img = self._get_starting_grid_img()
        starting_grid_pos = paste(starting_grid_img, img, (width - starting_grid_img.width), top=content_config.get('starting_grid', {}).get('padding_top', 22))
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

    def _get_starting_grid_img(self):
        config = self.visual_config['right_content'].get('starting_grid', {})
        font = FontFactory.get_font(config.get('font_name'),
                                             config.get('font_size', 50),
                                             FontFactory.black)
        color = config.get('font_color', (0,0,0))
        return text('STARTING GRID', color, font)

    def _get_result_img(self, width:int, height:int, result:RaceRankingRow):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        rows_config = self.visual_config['right_content'].get('rows', {})
        pos_config = rows_config.get('position', {})
        
        pos_img = Image.new('RGB', (pos_config.get('width', 156), height), (0,0,0))
        font = FontFactory.get_font(pos_config.get('font_name'), pos_config.get('font_size', 30),
                                    FontFactory.regular)
        font_color = pos_config.get('font_color', (255,255,255))
        pos_txt = get_ordinal_img_with_font(result.position, font, font_color)
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

        pilot_font = FontFactory.get_font(pos_config.get('font_name'), pos_config.get('font_size', 30),
                                    FontFactory.black)

        team_txt = text(pilot.name.upper(), pilot.team.standing_fg, pilot_font)
        paste(team_txt, img, team_name_pos.left+pilot_config.get('left_padding', 200))
        return img
