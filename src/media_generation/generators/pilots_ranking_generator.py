from PIL import Image
from ..generators.abstract_generator import AbstractGenerator

from ..helpers.transform import *
from ..font_factory import FontFactory
from ..models import Pilot, Team, Visual

RESERVIST_TEAM = Team(
    name='Reservist',
    title='Reservist',
    subtitle='Reservist',
    main_color=(215, 190, 50),
    secondary_color=(0, 0, 186),
    box_color=(0, 0, 186),
    standing_bg= (128,128,128),
    standing_fg = (220, 220, 220)
)

PILOTS_BY_COLUMN = 13

class PilotsRankingGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'ranking'

    def _get_visual_title_height(self, base_img: PngImageFile = None) -> int:
        return 200

    def _generate_basic_image(self) -> PngImageFile:
        width = (1080 * 2) + 60
        height = 1440
        return Image.new('RGB', (width, height), (0,0,0))

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        height = self._get_visual_title_height()
        with Image.open('assets/rankings/bg_top.png') as img:
            img = resize(img.copy().convert('RGB'), base_img.width, height, keep_ratio=False)

        left_img = self._generate_left_title_image(base_img.width // 3, height)
        left_img_pos = paste(left_img, img, use_obj=True, left=0)

        right_img = self._generate_right_title_image(int(2 * base_img.width / 3), height)
        paste(right_img, img, left=left_img_pos.right)

        return img

    def _generate_left_title_image(self, width:int, height:int) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        with Visual.get_fbrt_logo() as logo:
            logo = resize(logo, logo.width, img.height)
            paste(logo, img)
        return img

    def _generate_right_title_image(self, width:int, height:int) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        big_txt_content = self.config.ranking_title
        small_txt_content = self.config.ranking_subtitle

        big_txt_font = FontFactory.black(70)
        small_txt_font = FontFactory.regular(36)

        _, big_txt_expected_height = text_size(big_txt_content, big_txt_font, img)
        _, small_txt_expected_height = text_size(small_txt_content, small_txt_font, img)
        all_txt_height = big_txt_expected_height + small_txt_expected_height

        big_txt = text(big_txt_content, (0,0,0), big_txt_font)
        _, _, _, big_txt_bottom = paste(big_txt, img, top=(height-all_txt_height)//2)
        small_txt = text(small_txt_content, (0,0,0), small_txt_font)
        paste(small_txt, img, top=big_txt_bottom+20)
        return img

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
        padding_between_cols = 80
        padding_side = 20
        padding_top = 20
        width = base_img.width - 2 * padding_side
        row_height = ((base_img.height - title_height - padding_top) // PILOTS_BY_COLUMN) - padding_between_rows
        current_top = title_height+padding_top
        current_left = padding_side
        column_width = ((width - padding_between_cols)// 2)
        if self.config.metric == 'Total':
            data_type = int
        else:
            data_type = float
        self.config.ranking[self.config.metric] = self.config.ranking[self.config.metric].str.replace(',','.').astype(data_type)
        i = 0
        for _, row in self.config.ranking.sort_values(by=self.config.metric, ascending=False).iterrows():
            if i % PILOTS_BY_COLUMN == 0 and i > 0:
                current_top = title_height+padding_top
                current_left += column_width + padding_between_cols
            pilot_ranking_img = self._get_pilot_ranking_img(column_width, row_height, row['Pilot'], row[self.config.metric], i+1)
            _, _, _, r_bottom = paste(pilot_ranking_img, base_img, left=current_left, top=current_top)
            current_top = r_bottom + padding_between_rows
            i += 1

    def _get_pilot_ranking_img(self, width:int, height:int, pilot_name, points, pos):
        img = Image.new('RGBA', (width, height), (0,0,0,0))

        # [POS] [TEAM CARD + PILOT] [PTS]
        #  15%        65%            20%

        padding_between = 20
        effective_width = width - 2 * padding_between
        position_width = int(0.15 * effective_width)
        points_width = int(0.2 * effective_width)
        pilot_width = effective_width - position_width - points_width

        # POS
        pos_txt = self._get_pos_img(position_width, height, pos)
        pos_position = paste(pos_txt, img, left=0, use_obj=True)

        # TEAM
        pilot = self.config.pilots.get(pilot_name)
        if not pilot:
            pilot = Pilot(name=pilot_name, team=RESERVIST_TEAM, number='RE')
        team_card_img = self._get_team_card_img(pilot_width, height, pilot.team)
        team_name_left, _, team_name_right, _ = paste(team_card_img, img, left=pos_position.right+padding_between, with_alpha=False)

        # pilot name
        pilot_font = FontFactory.black(36 if PILOTS_BY_COLUMN >= 14 else 40)
        team_txt = text(pilot.name.upper(), pilot.team.standing_fg, pilot_font)
        paste(team_txt, img, team_name_left+225)

        # POINTS
        points_txt = self._get_points_img(points_width, height, str(points))
        paste(points_txt, img, left=team_name_right + padding_between)

        return img

    def _get_team_card_img(self, width:int, height: int, team:Team):
        with Image.open(f'assets/teams/empty_cards/{team.name}.png') as img:
            return img.copy()

    def _get_points_img(self, width:int, height: int, points:str):
        img = Image.new('RGB', (width, height), (255, 255, 255))
        font_size = self._determine_font_size(points, img, Font=FontFactory.black, initial_font_size=44)
        points_font = FontFactory.black(font_size)
        points_txt = text(points, (0,0,0), points_font)
        paste(points_txt, img, top=(height-points_txt.height)//2 - 4)
        return img

    def _get_pos_img(self, width:int, height: int, pos:int):
        pos = self._pos_to_ordinal(pos)
        img = Image.new('RGB', (width, height), (0, 0, 0))

        if PILOTS_BY_COLUMN < 11:
            font_size = 60
        elif PILOTS_BY_COLUMN < 13:
            font_size = 50
        else:
            font_size = 44
        pos_font = FontFactory.regular(font_size)
        pos_txt = text(pos, (255,255,255), pos_font)
        paste(pos_txt, img)
        return img

    def _pos_to_ordinal(self, n):
        suffix = {1: 'ST', 2: 'ND', 3: 'RD'}.get(4 if 10 <= n % 100 < 20 else n % 10, "TH")
        return f'{n}{suffix}'

    def _determine_font_size(self, text, img, Font=FontFactory.regular, initial_font_size=20):
        font_size = initial_font_size
        txt_width, txt_height = text_size(text, Font(font_size), img)
        height_offset = 10
        while txt_width <= img.width-height_offset and txt_height <= img.height-height_offset:
            font_size += 1
            txt_width, txt_height = text_size(text, Font(font_size), img)
        while txt_width >= img.width and txt_height >= img.height:
            font_size -= 1
            txt_width, txt_height = text_size(text, Font(font_size), img)
        return font_size + 1
