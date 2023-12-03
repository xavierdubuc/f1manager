from PIL import Image
from PIL.PngImagePlugin import PngImageFile
import logging

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

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        if self.visual_config.get('title_height', 0) == 0:
            return
        return super()._generate_title_image(base_img)

    def _get_visual_title_height(self, base_img: PngImageFile = None) -> int:
        return self.visual_config['title_height']

    def _generate_basic_image(self) -> PngImageFile:
        width = self.visual_config['width']
        height = self.visual_config['height']
        img = Image.new('RGB', (width, height), (255, 255, 255))
        bg = self._get_background_image()
        if bg:
            with bg:
                bg = resize(bg, width, height)
                paste(bg.convert('RGB'), img)
        return img

    def _add_content(self, final: PngImageFile):
        title_height = self._get_visual_title_height()
        paddings = self.visual_config['padding']
        top_h_padding = paddings['top']
        available_width = final.width - paddings['left']
        subtitle_image = self._get_subtitle_image(
            available_width, self.visual_config['subtitle']['height'])
        pos = paste(subtitle_image, final,
                    paddings['left'], title_height + top_h_padding)

        rankings_top = pos.bottom + \
            self.visual_config['content']['padding']['top']
        rankings_height = final.height - rankings_top
        rankings_img = self._get_ranking_image(final.width, rankings_height)
        paste(rankings_img, final, left=0, top=rankings_top)

    def _get_subtitle_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        subtitle_config = self.visual_config['subtitle']
        padding = subtitle_config['padding']
        race_title_width = int(0.35 * width)

        name_font_size = subtitle_config['circuit_name']['font_size']
        name_font_name = subtitle_config['circuit_name'].get('font')
        if name_font_name:
            name_font = FontFactory.font(name_font_name, name_font_size)
        else:
            name_font = FontFactory.black(name_font_size)

        city_font_size = subtitle_config['circuit_city']['font_size']
        city_font_name = subtitle_config['circuit_city'].get('font')
        if city_font_name:
            city_font = FontFactory.font(city_font_name, city_font_size)
        else:
            city_font = FontFactory.black(city_font_size)

        race_date_font_size = subtitle_config['race_date']['font_size']
        race_date_font_name = subtitle_config['race_date'].get('font')
        if race_date_font_name:
            race_date_font = FontFactory.font(
                race_date_font_name, race_date_font_size)
        else:
            race_date_font = FontFactory.regular(race_date_font_size)

        race_title_image = self.race_renderer.get_circuit_and_date_img(
            race_title_width,
            height,
            name_font=name_font,
            city_font=city_font,
            date_font=race_date_font
        )
        race_dimension = paste(race_title_image, img, left=padding)

        fastest_lap_left = race_dimension.right + padding
        fastest_lap_width = width - padding - fastest_lap_left
        fastest_lap_img = self._get_fastest_lap_image(
            fastest_lap_width, height)
        paste(fastest_lap_img, img, fastest_lap_left)
        return img

    def _get_fastest_lap_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (30, 30, 30, 235))

        # FASTEST LAP IMG
        with Image.open(f'assets/fastest_lap.png') as fstst_img:
            fstst_img = resize(fstst_img, height, height)
            logo_pos = paste(fstst_img, img, left=0)

        # TEAM LOGO
        pilot = self.race.fastest_lap_pilot
        if not pilot:
            raise IncorrectDataException(
                f'Fastest lap pilot "{self.race.fastest_lap_pilot_name}" is unknown !')
        team = pilot.team
        with team.get_results_logo() as team_img:
            team_img = resize(team_img, height, height)
            team_pos = paste(team_img, img, left=logo_pos.right+20)

        # PILOT NAME
        pilot_font = FontFactory.get_font(
            self.visual_config['fastest_lap']['pilot'].get('font'),
            self.visual_config['fastest_lap']['pilot']['font_size'],
            FontFactory.bold
        )
        pilot_font_color = self.visual_config['fastest_lap']['pilot']['font_color']
        pilot_content = self.race.fastest_lap_pilot.name.upper()
        pilot_txt = text(pilot_content, pilot_font_color, pilot_font)
        pilot_pos = paste(pilot_txt, img, left=team_pos.right + 30)

        # LAP #
        lap_font = FontFactory.get_font(
            self.visual_config['fastest_lap']['lap'].get('font'),
            self.visual_config['fastest_lap']['lap']['font_size'],
            FontFactory.regular
        )
        lap_font_color = self.visual_config['fastest_lap']['lap']['font_color']
        lap_txt_content = self.visual_config['fastest_lap']['lap']['text']
        if not self.race.fastest_lap_lap:
            _logger.warning('Fastest lap "LAP" information is not filled in !')
        lap_content = f'{lap_txt_content} {self.race.fastest_lap_lap}'
        lap_txt = text(lap_content, lap_font_color, lap_font)
        lap_left_space = self.visual_config['fastest_lap']['lap']['left']
        paste(lap_txt, img, left=pilot_pos.right + lap_left_space)

        # LAP TIME
        time_font = FontFactory.get_font(
            self.visual_config['fastest_lap']['time'].get('font'),
            self.visual_config['fastest_lap']['time']['font_size'],
            FontFactory.bold
        )
        time_font_color = self.visual_config['fastest_lap']['time']['font_color']
        if not self.race.fastest_lap_time or self.race.fastest_lap_time == DEFAULT_TIME:
            _logger.warning('Fastest lap "TIME" information is not filled in !')
        time_txt = text(self.race.fastest_lap_time, time_font_color, time_font)
        paste(time_txt, img, left=width-time_txt.width-15)

        return img

    def _get_ranking_image(self, width: int, height: int):
        content_config = self.visual_config['content']
        img = Image.new('RGBA', (width, height), content_config['background'])
        top = content_config['top']
        hop_between_position = content_config['hop_between']
        row_height = content_config['row_height']
        padding_left = self.visual_config['content']['padding']['left']
        padding_between = self.visual_config['content']['padding']['between_cols']
        padding_right = self.visual_config['content']['padding']['right']
        col_width = (width - (padding_left+padding_between+padding_right)) // 2
        first_col_left = padding_left
        second_col_left = padding_left + col_width + padding_between

        maximum_split_size, maximum_tyre_amount = self._compute_max_split_size_and_tyre_amount()

        if not self.race.race_result or not self.race.race_result.rows:
            raise IncorrectDataException('No race results !')
        for ranking_row in self.race.race_result.rows:
            if not ranking_row.pilot:
                raise IncorrectDataException(f'Invalid pilot "{ranking_row.position}. {ranking_row.pilot_name}"')
            row_renderer = RankingRowRenderer(
                ranking_row,
                self.championship_config['settings']['components']['ranking_row_renderer']
            )

            left = first_col_left if ranking_row.position % 2 == 1 else second_col_left
            pilot_result_image = row_renderer.get_details_image(
                col_width,
                row_height,
                maximum_split_size,
                maximum_tyre_amount
            )
            paste(pilot_result_image, img, left, top)
            top += hop_between_position
        return img

    def _compute_max_split_size_and_tyre_amount(self):
        maximum_split_size = 0
        maximum_tyre_amount = 0
        for ranking_row in self.race.race_result.rows:
            # compute max size of time & split
            if ranking_row.split is not None:
                w, _ = text_size(ranking_row.split, small_font)
                if w > maximum_split_size:
                    maximum_split_size = w
            # compute max amount of tyre stints
            if ranking_row.tyres is not None:
                tyre_amount = len(ranking_row.tyres)
                if tyre_amount > maximum_tyre_amount:
                    maximum_tyre_amount = tyre_amount
        return maximum_split_size, maximum_tyre_amount
