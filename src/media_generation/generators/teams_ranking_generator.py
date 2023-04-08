from PIL import Image
from ..generators.abstract_generator import AbstractGenerator

from ..helpers.transform import *
from ..font_factory import FontFactory
from ..models import Team, Visual
from ..data import teams_idx

class TeamsRankingGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'ranking'

    def _generate_basic_image(self) -> PngImageFile:
        width = 1080
        height = 1440
        return Image.new('RGB', (width, height), (0,0,0))

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        height = 300
        with Image.open('assets/rankings/bg_top.png') as img:
            img = resize(img.copy().convert('RGB'), base_img.width, height, keep_ratio=False)

        with Visual.get_fbrt_logo() as logo:
            logo = resize(logo, logo.width, img.height//2)
            _, _, _, logo_bottom = paste(logo, img, top=10)

        big_txt_font = FontFactory.black(60)
        big_txt = text(self.config.ranking_title, (0,0,0), big_txt_font)
        _, _, _, big_txt_bottom = paste(big_txt, img, top=logo_bottom+10)

        small_txt_font = FontFactory.regular(30)
        small_txt = text(self.config.ranking_subtitle, (0,0,0), small_txt_font)
        paste(small_txt, img, top=big_txt_bottom+20)

        return img


    def _add_content(self, base_img: PngImageFile):
        title_height = 300
        width = base_img.width - 40
        padding_between_rows = 25
        padding_top = 20
        row_height = ((base_img.height - 300 - padding_top) // 10) - padding_between_rows
        # row_height = 87
        current_top = title_height+padding_top
        for _, row in self.config.ranking.iterrows():
            team_ranking_img = self._get_team_ranking_img(width, row_height, row['Ecurie'], row['Total'])
            _, _, _, r_bottom = paste(team_ranking_img, base_img, top=current_top)
            current_top = r_bottom + padding_between_rows

    def _get_team_ranking_img(self, width:int, height:int, team_name, points):
        img = Image.new('RGBA', (width, height), (0,0,0,0))

        # TEAM
        team = teams_idx[team_name]
        team_img = self._get_team_img((2 * width) // 3, height, team)
        _, _, team_name_right, _ = paste(team_img, img, left=0)

        # POINTS
        points_txt = self._get_points_img(width // 3, height, points)
        paste(points_txt, img, left=team_name_right + 25)

        return img

    def _get_team_img(self, width:int, height: int, team:Team):
        with Image.open(f'assets/teams/cards/{team.name}.png') as img:
            return img.copy()
        img = Image.new('RGB', (width, height), team.standing_bg)
        # logo
        with Image.open(team.get_image()) as logo:
            logo = resize(logo.copy(), width//3, height-10)
            _, _, logo_right, _ = paste(logo, img, left=10)

        #text
        team_font = FontFactory.black(54)
        team_txt = text(team.title.upper(), team.standing_fg, team_font)
        paste(team_txt, img, logo_right+40)
        return img

    def _get_points_img(self, width:int, height: int, points:str):
        img = Image.new('RGB', (width, height), (255, 255, 255))
        points_font = FontFactory.black(80)
        points_txt = text(points, (0,0,0), points_font)
        paste(points_txt, img)
        return img