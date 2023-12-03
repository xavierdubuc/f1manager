from PIL import Image
from PIL.PngImagePlugin import PngImageFile

from src.media_generation.models.visual import Visual
from ..generators.abstract_race_generator import AbstractRaceGenerator
from ..helpers.transform import *


class LineupGenerator(AbstractRaceGenerator):
    def _get_visual_type(self) -> str:
        return 'lineups'

    def _generate_basic_image(self) -> PngImageFile:
        return Image.new('RGB', (1920, 1080), (255,255,255))

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        return None

    def _add_content(self, base_img: PngImageFile):
        draw_lines_all(base_img, (200,200,200), space_between_lines=7)
        amount_of_teams_by_column = 5
        teams_width = int(.38 * base_img.width) #should be near 730
        teams_height = int(.195 * base_img.height)  # should be near 210
        teams_left = 5
        teams_top = teams_initial_top = 2
        teams_margin = 5

        center_width = base_img.width - teams_width * 2

        for i, team in enumerate(self.config.teams):
            lineup_img = team.get_lineup_image(teams_width, teams_height, self.race.get_pilots(team))
            teams_pos = paste(lineup_img, base_img, left=teams_left, top=teams_top)
            if i == amount_of_teams_by_column - 1:
                teams_top = teams_initial_top
                teams_left += teams_width + center_width - 10
            else:
                teams_top = teams_pos.bottom + teams_margin

        padding = 25
        center_img = self._get_center_image(center_width-2*padding, base_img.height)
        paste(center_img, base_img, left=teams_width + padding)

    def _get_center_image(self, width:int, height:int) -> PngImageFile:
        circuit = self.race.circuit
        img = Image.new('RGB', (width, height), (255,255,255))

        # FBRT
        fbrt_logo_size = int(0.8 * width)
        fbrt_logo = resize(Visual.get_fbrt_round_logo(), fbrt_logo_size)
        fbrt_logo_pos = paste(fbrt_logo, img, top=0)

        # COURSE X + TITLE 'LINE-UP'
        type_title_top = fbrt_logo_pos.bottom+50
        type_size = int(0.35 * width)
        padding_type_title = 20
        type_img = self.race_renderer.get_type_image(
            type_size, type_size, text_font=FontFactory.regular(20)
        )
        title_line1_text = 'LINE'
        title_line2_text = '   UP'
        title_line1_img = text(title_line1_text, (0,0,0), FontFactory.black(60))
        title_line2_img = text(title_line2_text, (0,0,0), FontFactory.black(60))
        whole_line_width = type_img.width + title_line1_img.width+padding_type_title
        type_pos = paste(type_img, img, left=(width-whole_line_width)//2, top=type_title_top)
        # TITLE "LINE-UP"
        space_between_lines = 10
        title_height = title_line1_img.height+title_line2_img.height+space_between_lines
        title_line1_pos = paste(title_line1_img, img, left=type_pos.right+padding_type_title, top=type_pos.top + (type_img.height-title_height)//2)
        paste(title_line2_img, img, left=type_pos.right+padding_type_title, top=title_line1_pos.bottom+space_between_lines)

        # CIRCUIT FLAG
        flag_top = type_pos.bottom + 50
        flag_height = 100
        with circuit.get_flag() as flag_img:
            flag_img = resize(flag_img, height=flag_height)
            flag_pos = paste(flag_img, img, top=flag_top)

        # CIRCUIT INFO (NAME + CITY + DATE)
        circuit_top = flag_pos.bottom + 20
        circuit_padding = 15

        # Create image so we can have the needed size for black BG
        circuit_name_img = circuit.get_name_img(FontFactory.black(34))
        padding_name_city = 5
        padding_city_date = 20
        circuit_city_img = circuit.get_city_img(FontFactory.black(28))
        date_txt = f'{self.race.day} {date_fr(self.race.month).upper()}'
        date_img = text(date_txt, (255, 255, 255), FontFactory.regular(30))
        circuit_height = (
            circuit_name_img.height
            + padding_name_city
            + circuit_city_img.height
            + padding_city_date
            + date_img.height
            + (circuit_padding * 2)
        )
        # --- BLACK BG
        circuit_bg = Image.new('RGB', (width, circuit_height), (0,0,0))
        circuit_bg_pos = paste(circuit_bg, img, top=circuit_top)

        circuit_name_pos = paste(circuit_name_img, img, top=circuit_bg_pos.top+circuit_padding)
        city_pos = paste(circuit_city_img, img, top=circuit_name_pos.bottom+padding_name_city)
        paste(date_img, img, top=city_pos.bottom+padding_city_date)

        # F1
        f1_logo_size = int(0.7 * width)
        with Visual.get_f1_logo('black') as f1_logo_img:
            f1_logo_img = resize(f1_logo_img, f1_logo_size, f1_logo_size)
            f1_logo_pos = paste(f1_logo_img, img, top=img.height - f1_logo_img.height - 40)

        # FIF
        fif_logo_size = int(0.7 * width)
        with Visual.get_fif_logo('wide') as fif_logo_img:
            fif_logo_img = resize(fif_logo_img, fif_logo_size, fif_logo_size)
            paste(fif_logo_img, img, top=f1_logo_pos.top - fif_logo_img.height)
        return img
    