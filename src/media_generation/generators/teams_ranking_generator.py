import logging
from PIL import Image
from ..generators.abstract_generator import AbstractGenerator

from ..helpers.transform import *
from ..font_factory import FontFactory
from ..models import Team, Visual
from ..data import teams_idx

_logger = logging.getLogger(__name__)

class TeamsRankingGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'teams_ranking'

    def _generate_basic_image(self) -> PngImageFile:
        width = self.visual_config['width']
        height = self.visual_config['height']
        _logger.info(f'Output size is {width}px x {height}px')
        # FIXME use a BG image ?
        return Image.new('RGB', (width, height), (255,255,255))

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        height = 300
        img = Image.new('RGB', (base_img.width,height), (255,255,255))

        # LEFT LOGO
        left_logo_config = self.visual_config.get('left_logo')
        if left_logo_config:
            with Image.open(left_logo_config['path']) as left_logo:
                left_logo = resize(left_logo, height=left_logo_config['height'])
            logo_pos = paste(left_logo, img, left=left_logo_config['left'])

        # RIGHT LOGO
        right_logo_config = self.visual_config.get('right_logo')
        if right_logo_config:
            right_padding_top = right_logo_config['padding_top']
            with Image.open(right_logo_config['path']) as right_logo:
                right_logo = resize(right_logo, height=right_logo_config['height'])
            paste(right_logo, img, left=img.width-right_logo.width, top=height-right_logo.height - right_padding_top)

        # Main title
        title_cfg = self.visual_config['title']
        font_size = title_cfg.get('font_size', 60)
        font_color = title_cfg.get('font_color', (0,0,0))
        font_name = title_cfg.get('font')
        txt_font = FontFactory.get_font(font_name, font_size, FontFactory.black)

        parts = self.config.ranking_title.split(' ')
        title_parts = [' '.join(parts[:2])] + parts[2:]
        txt_left = logo_pos.right + title_cfg['padding_left']
        txt_top = title_cfg['top']

        for title_part in title_parts:
            big_txt = text(title_part, font_color, txt_font)
            big_txt_pos = paste(big_txt, img, left=txt_left, top=txt_top)
            txt_top = big_txt_pos.bottom+10

        # Sub title
        if self.config.ranking_subtitle:
            small_font_size = title_cfg.get('small_font_size', 30)
            small_font_color = title_cfg.get('small_font_color', (0,0,0))
            small_font_name = title_cfg.get('small_font')
            small_txt_font = FontFactory.get_font(small_font_name, small_font_size, FontFactory.regular)
            small_txt = text(self.config.ranking_subtitle, small_font_color, small_txt_font)
            paste(small_txt, img, left=txt_left, top=big_txt_pos.bottom+20)

        return img

    def _add_content(self, base_img: PngImageFile):
        title_height = 300
        width = base_img.width - 40
        padding_between_rows = 25
        padding_top = 20
        row_height = ((base_img.height - 300 - padding_top) // 10) - padding_between_rows
        # row_height = 87
        current_top = title_height+padding_top
        for i, row in enumerate(self.config.ranking):
            is_champion = False # FIXME
            team_ranking_img = self._get_team_ranking_img(width, row_height, row.team_name, row.total_points, is_champion)
            pos = paste(team_ranking_img, base_img, top=current_top)
            current_top = pos.bottom + padding_between_rows

    def _get_team_ranking_img(self, width:int, height:int, team_name, points, is_champion: bool = False):
        img = Image.new('RGBA', (width, height), (0,0,0,0))

        # TEAM
        team = teams_idx[team_name]
        team_img = self._get_team_img((2 * width) // 3, height, team)
        pos = paste(team_img, img, left=0)

        # POINTS
        color = (199, 141, 39) if is_champion else (255,255,255)
        points_txt = self._get_points_img(width // 3, height, points, color)
        paste(points_txt, img, left=pos.right + 25)

        return img

    def _get_team_img(self, width:int, height: int, team:Team):
        card = team.build_card_image(width, height)

        cfg = self.visual_config['rows']['team']
        font_name = cfg.get('font')
        font_size = cfg.get('font_size', 54)
        font_color = team.standing_fg
        font = FontFactory.get_font(font_name, font_size, FontFactory.black)
        left = cfg.get('left', 0)
        top = cfg.get('top', False)

        team_name = text(team.title, font_color, font)
        paste(team_name, card, left=left, top=top)

        return card

    def _get_points_img(self, width:int, height: int, points:str, color:tuple = None):
        img = Image.new('RGB', (width, height), (0,0,0))

        cfg = self.visual_config['rows']['points']
        font_name = cfg.get('font')
        font_size = cfg.get('font_size', 70)
        font_color = color or cfg['font_color']
        font = FontFactory.get_font(font_name, font_size, FontFactory.black)

        points_top = cfg.get('top', 0)
        points_txt = text(str(points), font_color, font)
        paste(points_txt, img, top=points_top)
        return img