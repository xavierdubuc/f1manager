from PIL import Image
from PIL.PngImagePlugin import PngImageFile
import logging

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

    # TITLE

    def _get_customized_title_image(self,  base_img: PngImageFile, title_config:dict) -> PngImageFile:
        img = super()._get_customized_title_image(base_img, title_config)

        txt = self._get_customized_title_text_image(base_img, title_config)
        left = title_config.get('text_left', False)
        top = title_config.get('text_top', False)
        paste(txt, img, left=left, top=top)

        if f1_config := title_config.get('f1_logo', None):
            f1_logo = self._get_customized_title_f1logo_image(base_img, f1_config)
            f1_logo_left = f1_config.get('left', base_img.width-f1_logo.width)
            f1_logo_top = f1_config.get('top', False)
            paste(f1_logo, img, left=f1_logo_left, top=f1_logo_top)

        champ_config = title_config.get('champ_logo', None)
        champ_logo = self._get_customized_title_champ_logo_image(base_img, champ_config)
        champ_logo_left = champ_config.get('left', base_img.width-champ_logo.width)
        champ_logo_top = champ_config.get('top', False)
        paste(champ_logo, img, left=champ_logo_left, top=champ_logo_top)

        return img

    def _get_customized_title_text_image(self,  base_img: PngImageFile, title_config:dict) -> PngImageFile:
        font = FontFactory.get_font(
            title_config.get('font'),
            title_config.get('font_size', 74),
            FontFactory.black
        )
        txt = title_config.get('content', 'Results').upper()
        color = title_config.get('font_color', (255, 255, 255))
        return text(txt, color, font)

    def _get_customized_title_f1logo_image(self,  base_img: PngImageFile, config:dict) -> PngImageFile:
        # F1 23
        with Visual.get_f1_logo(config['color']) as f1:
            if w := config.get('width'):
                logo = resize(f1, width=w)
            else:
                logo = resize(f1, height=self._get_visual_title_height())
        return logo

    def _get_customized_title_champ_logo_image(self,  base_img: PngImageFile, config:dict) -> PngImageFile:
        # F1 23
        with Image.open(config['path']) as champ:
            if w := config.get('width'):
                logo = resize(champ, width=w)
            else:
                logo = resize(champ, height=self._get_visual_title_height())
        return logo

    def _add_content(self, final: PngImageFile):
        title_height = self._get_visual_title_height()
        paddings = self.visual_config['padding']
        top_h_padding = paddings['top']
        available_width = final.width - paddings['left']
        subtitle_image = self._get_subtitle_image(
            available_width, self.visual_config['subtitle']['height']
        )
        pos = paste(
            subtitle_image, final, paddings['left'], title_height + top_h_padding
        )

        rankings_top = pos.bottom + self.visual_config['content']['padding']['top']
        rankings_height = final.height - rankings_top
        rankings_img = self._get_ranking_image(final.width, rankings_height)
        paste(rankings_img, final, left=0, top=rankings_top)

    def _get_subtitle_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        config = self.visual_config['subtitle']
        padding = config['padding']
        race_title_width = int(0.35 * width)

        circuit_name_cfg = config['circuit_name']
        name_font = FontFactory.get_font(
            circuit_name_cfg.get('font'),
            circuit_name_cfg['font_size'],
            FontFactory.black
        )
        circuit_city_cfg = config['circuit_city']
        city_font = FontFactory.get_font(
            circuit_city_cfg.get('font'),
            circuit_city_cfg['font_size'],
            FontFactory.black
        )
        race_date_cfg = config['race_date']
        race_date_font = FontFactory.get_font(
            race_date_cfg.get('font'),
            race_date_cfg['font_size'],
            FontFactory.regular
        )

        round_img = self.race_renderer.get_type_image(height, height, with_txt=False)
        race_title_image = self.race_renderer.get_circuit_and_date_img(
            race_title_width,
            height,
            name_font=name_font,
            name_color=circuit_name_cfg.get('color'),
            city_font=city_font,
            city_color=circuit_city_cfg.get('color'),
            date_font=race_date_font,
            date_color=race_date_cfg.get('color'),
            name_top=circuit_name_cfg.get('top', 10),
            city_top=circuit_city_cfg.get('top', 50),
            date_top=race_date_cfg.get('top', 0),
        )
        round_dim = paste(round_img, img, left=padding)
        if bgcolor := config.get('background'):
            bg = Image.new('RGBA', (race_title_image.width, race_title_image.height), bgcolor)
            paste(bg, img, left=round_dim.right)
        race_pos = paste(race_title_image, img, left=round_dim.right+padding)

        fastest_lap_left = race_pos.right + padding
        fastest_lap_width = width - padding - fastest_lap_left
        fastest_lap_img = self._get_fastest_lap_image(
            fastest_lap_width, height
        )
        paste(fastest_lap_img, img, fastest_lap_left)
        return img

    def _get_fastest_lap_image(self, width: int, height: int):
        fl_config = self.visual_config['fastest_lap']
        bgcolor = fl_config.get('background', (30, 30, 30, 235))
        img = Image.new('RGBA', (width, height), bgcolor)

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
        pilot_config = fl_config['pilot']
        pilot_font = FontFactory.get_font(
            pilot_config.get('font'),
            pilot_config['font_size'],
            FontFactory.bold
        )
        pilot_font_color = pilot_config['font_color']
        pilot_content = self.race.fastest_lap_pilot.name.upper()
        pilot_txt = text(pilot_content, pilot_font_color, pilot_font)
        pilot_pos = paste(pilot_txt, img, left=team_pos.right + 30, top=pilot_config['top'])

        # LAP #
        lap_config = fl_config['lap']
        lap_font = FontFactory.get_font(
            lap_config.get('font'),
            lap_config['font_size'],
            FontFactory.regular
        )
        lap_font_color = lap_config['font_color']
        lap_txt_content = lap_config['text']
        if not self.race.fastest_lap_lap:
            _logger.warning('Fastest lap "LAP" information is not filled in !')
        lap_content = f'{lap_txt_content} {self.race.fastest_lap_lap}'
        lap_txt = text(lap_content, lap_font_color, lap_font)
        lap_left_space = lap_config['left']
        paste(lap_txt, img, left=pilot_pos.right + lap_left_space, top=lap_config['top'])

        # LAP TIME
        time_config = fl_config['time']
        time_font = FontFactory.get_font(
            time_config.get('font'),
            time_config['font_size'],
            FontFactory.bold
        )
        time_font_color = time_config['font_color']
        if not self.race.fastest_lap_time or self.race.fastest_lap_time == DEFAULT_TIME:
            _logger.warning('Fastest lap "TIME" information is not filled in !')
        time_txt = text(self.race.fastest_lap_time, time_font_color, time_font)
        paste(time_txt, img, left=width-time_txt.width-15, top=time_config['top'])

        return img

    def _get_ranking_image(self, width: int, height: int):
        content_config = self.visual_config['content']
        img = Image.new('RGBA', (width, height), content_config['background'])
        top = content_config['top']
        hop_between_position = content_config['hop_between']
        row_height = content_config['row_height']
        content_paddings = content_config['padding']
        padding_left = content_paddings['left']
        padding_between = content_paddings['between_cols']
        padding_right = content_paddings['right']
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
