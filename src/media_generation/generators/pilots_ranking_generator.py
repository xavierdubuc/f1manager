import logging
from PIL import Image

from src.media_generation.helpers.generator_config import GeneratorConfig
from ..generators.abstract_generator import AbstractGenerator

from ..helpers.transform import *
from ..font_factory import FontFactory
from ..models import Pilot, Team, Visual

_logger = logging.getLogger(__name__)


class PilotsRankingGenerator(AbstractGenerator):
    def __init__(self, championship_config: dict, config: GeneratorConfig, season: int, identifier: str = None, *args, **kwargs):
        super().__init__(championship_config, config, season, identifier, *args, **kwargs)
        key = self.identifier or 'default'
        cfg = self.visual_config['body']
        self.rows_config = cfg.get(key, cfg['default'])

    def _get_visual_type(self) -> str:
        return 'pilots_ranking'

    def _get_visual_title_height(self, base_img: PngImageFile = None) -> int:
        return 200

    def _generate_basic_image(self) -> PngImageFile:
        width = self.visual_config['width']
        height = self.visual_config['height']
        _logger.info(f'Output size is {width}px x {height}px')
        # FIXME use a BG image ?
        return Image.new('RGB', (width, height), (0,0,0))

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        #                 base_img.width
        # <---------------------------------------------->
        # LEFT LOGO        TITLE TEXT        [RIGHT LOGO]
        height = self._get_visual_title_height()
        img = Image.new('RGB', (base_img.width,height), (255,255,255))

        # TITLE TEXT
        title_img, title_pos = self._generate_ranking_title_image(base_img.width, height)
        paste(title_img, img)

        # LEFT LOGO
        left_logo_config = self.visual_config.get('left_logo')
        if left_logo_config:
            with Image.open(left_logo_config['path']) as left_logo:
                left_logo = resize(left_logo, height=left_logo_config['height'])
            paste(left_logo, img, left=(title_pos.left - left_logo.width) // 2)

        # RIGHT LOGO
        right_logo_config = self.visual_config.get('right_logo')
        if right_logo_config:
            right_padding_top = right_logo_config['padding_top']
            with Image.open(right_logo_config['path']) as right_logo:
                right_logo = resize(right_logo, height=right_logo_config['height'])
            paste(right_logo, img, left=img.width-right_logo.width, top=height-right_logo.height - right_padding_top)
        return img

    def _generate_ranking_title_image(self, width:int, height:int) -> PngImageFile:
        #                 base_img.width
        # <---------------------------------------------->
        #                    BIG TXT
        #                   SMALL TXT
        img = Image.new('RGBA', (width, height), (0,0,0,0))

        # Main title
        big_txt_content = self.config.ranking_title
        if self.identifier == 'reservists':
            big_txt_content = f'Saison {self.season} classement réservistes'.upper()
        font_size = self.visual_config['title'].get('font_size', 70)
        font_color = self.visual_config['title'].get('font_color', (0,0,0))
        font_name = self.visual_config['title'].get('font')
        if font_name:
            big_txt_font = FontFactory.font(font_name, font_size)
        else:
            big_txt_font = FontFactory.black(font_size)

        # Sub title
        small_txt_content = self.config.ranking_subtitle
        small_font_size = self.visual_config['title'].get('small_font_size', 70)
        small_font_color = self.visual_config['title'].get('small_font_color', (0,0,0))
        small_font_name = self.visual_config['title'].get('small_font')
        small_txt_font = FontFactory.get_font(small_font_name, small_font_size, FontFactory.black)

        # Paste titles
        _, big_txt_expected_height = text_size(big_txt_content, big_txt_font, img)
        _, small_txt_expected_height = text_size(small_txt_content, small_txt_font, img)
        all_txt_height = big_txt_expected_height + small_txt_expected_height

        # -- main
        big_txt = text(big_txt_content, font_color, big_txt_font)
        vertical_adjustment = self.visual_config['title'].get('vertical_adjustment', 0)
        big_txt_pos = paste(big_txt, img, top=(height-all_txt_height)//2 + vertical_adjustment)

        # -- small
        small_txt = text(small_txt_content, small_font_color, small_txt_font)
        paste(small_txt, img, top=big_txt_pos.bottom+20)
        return img, big_txt_pos

    def _add_content(self, base_img: PngImageFile):
        #                 base_img.width
        # <---------------------------------------------->
        # |    || PILOT | PTS ||    || PILOT | PTS ||    |
        # <----><-------------><----><-------------><---->
        #   pds   column_width  pds+  column_width   pds
        #
        # <----><-----------------------------------><---->
        #   pds                 width                  pds
        #
        # column_width = width-pds // 2
        title_height = self._get_visual_title_height()
        padding_between_rows = 20
        padding_between_cols = 40
        padding_side = 20
        padding_top = 20
        width = base_img.width - 2 * padding_side
        row_height = ((base_img.height - title_height - padding_top) // self.rows_config['pilots_by_column']) - padding_between_rows
        current_top = title_height+padding_top
        current_left = padding_side
        amount_of_columns = self.rows_config['amounts_of_column']
        column_width = ((width - padding_between_cols)// amount_of_columns)
        if self.config.metric == 'Total':
            data_type = int
        else:
            data_type = float
        self.config.ranking[self.config.metric] = self.config.ranking[self.config.metric].str.replace(',','.').astype(data_type)
        amount_by_column = self.rows_config['pilots_by_column']
        i = 0
        max_pilot_index = (amount_of_columns * amount_by_column) - 1
        for _, row in self.config.ranking.sort_values(by=self.config.metric, ascending=False).iterrows():
            pilot = self.config.pilots.get(row['Pilot'])
            if not pilot:
                reservist_team = Team(**self.championship_config['settings']['reservist_team'])
                pilot = Pilot(name=row['Pilot'], team=reservist_team, number='RE', reservist=True)
            if (self.identifier == 'main' and pilot.reservist) or (self.identifier == 'reservists' and not pilot.reservist):
                continue
            if i % amount_by_column == 0 and i > 0:
                current_top = title_height+padding_top
                current_left += column_width + padding_between_cols
            pilot_ranking_img = self._get_pilot_ranking_img(column_width, row_height, pilot, row[self.config.metric], i+1)
            pilot_ranking_pos = paste(pilot_ranking_img, base_img, left=current_left, top=current_top)
            current_top = pilot_ranking_pos.bottom + padding_between_rows
            i += 1
            if i > max_pilot_index:
                break

    def _get_pilot_ranking_img(self, width:int, height:int, pilot:Pilot, points, pos):
        img = Image.new('RGBA', (width, height), (0,0,0,0))

        # [POS] [TEAM CARD + PILOT] [PTS]
        #  15%        65%            20%

        padding_between = 10
        effective_width = width - 2 * padding_between
        position_width = int(0.15 * effective_width)
        points_width = int(0.2 * effective_width)
        pilot_width = effective_width - position_width - points_width

        # POS
        pos_txt = self._get_pos_img(position_width, height, pos)
        pos_position = paste(pos_txt, img, left=0)

        # TEAM
        team_card_img = pilot.team.build_card_image(pilot_width, height)
        team_name_pos = paste(team_card_img, img, left=pos_position.right+padding_between, with_alpha=False)

        # pilot name
        pilot_config = self.rows_config['pilot']
        pilot_font_name = pilot_config.get('font')
        pilot_font_size = pilot_config['font_size']
        small_font_size_config = pilot_config.get('small_font')
        if small_font_size_config:
            if len(pilot.name) >= small_font_size_config['if']:
                pilot_font_size = small_font_size_config['size']
        pilot_font = FontFactory.get_font(pilot_font_name, pilot_font_size, FontFactory.black)
        team_txt = text(pilot.name.upper(), pilot.team.standing_fg, pilot_font)
        paste(team_txt, img, team_name_pos.left+pilot_config['left_padding'])

        # POINTS
        points_txt = self._get_points_img(points_width, height, str(points))
        paste(points_txt, img, left=team_name_pos.right + padding_between)

        return img

    def _get_points_img(self, width:int, height: int, points:str):
        img = Image.new('RGB', (width, height), (255, 255, 255))

        font_name = self.rows_config['points'].get('font')
        font_size = self.rows_config['points']['font_size']
        font = FontFactory.get_font(font_name, font_size, FontFactory.black)

        points_txt = text(points, (0,0,0), font, security_padding=4)
        paste(points_txt, img, top=(height-points_txt.height)//2 - 4)
        return img

    def _get_pos_img(self, width:int, height: int, pos:int):
        pos = self._pos_to_ordinal(pos)
        img = Image.new('RGB', (width, height), (0, 0, 0))

        font_name = self.rows_config['position'].get('font')
        font_size = self.rows_config['position']['font_size']
        font = FontFactory.get_font(font_name, font_size, FontFactory.regular)
        pos_txt = text(pos, (255,255,255), font)
        paste(pos_txt, img)
        return img

    def _pos_to_ordinal(self, n):
        ordinal_lang = self.championship_config['settings'].get('ordinal_lang', 'en')
        if ordinal_lang == 'en':
            suffix = {1: 'ST', 2: 'ND', 3: 'RD'}.get(4 if 10 <= n % 100 < 20 else n % 10, "TH")
        elif ordinal_lang == 'fr':
            suffix = {1: 'ER'}.get(n, "È")
        return f'{n}{suffix}'
