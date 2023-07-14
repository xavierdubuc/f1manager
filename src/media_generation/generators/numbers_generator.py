
import os.path
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from ..models import Pilot
from ..helpers.transform import *
from ..generators.abstract_generator import AbstractGenerator

MAX_NUMBER = 99

OFFICIAL_PILOTS_NUMBERS = {
    '1': '-',
    '2': 'Sargeant',
    '4': 'Norris',
    '10': 'Gasly',
    '11': 'Perez',
    '14': 'Alonso',
    '16': 'Leclerc',
    '17': '/',
    '18': 'Stroll',
    '20': 'Magnussen',
    '21': 'de Vries',
    '22': 'Tsunoda',
    '23': 'Albon',
    '24': 'Zhou',
    '27': 'Hulkenberg',
    '31': 'Ocon',
    '33': 'Verstappen',
    '44': 'Hamilton',
    '55': 'Sainz',
    '63': 'Russell',
    '77': 'Bottas',
    '81': 'Piastri'
}


class NumbersGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'numbers'

    def _get_visual_title_height(self, base_img: PngImageFile = None) -> int:
        return 200

    def _get_background_image(self) -> PngImageFile:
        path = os.path.join('assets/backgrounds', self.championship_config['name'], 'numbers.png')
        return Image.open(path)

    def _generate_basic_image(self) -> PngImageFile:
        width = (1080 * 2) + 60
        height = 1440
        img = Image.new('RGB', (width, height), (255, 255, 255))
        with self._get_background_image() as bg:
            paste(bg.convert('RGB'),img)

        lines_config = self.visual_config.get('lines', {})
        if lines_config.get('enabled', False):
            draw_lines_all(img, lines_config['color'], space_between_lines=lines_config['space'], line_width=lines_config['width'])
        return img

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        return None

    def _get_pilot_font_size(self, name):
        if len(name) > 15:
            return 16
        if len(name) > 13:
            return 18
        return 20

    def _add_content(self, base_img: PngImageFile):
        left_padding = 50
        top_padding = 40
        left = left_padding
        top = top_padding
        amount_of_columns = 5
        amount_of_lines_by_column = 20
        space_between_lines = 15
        space_between_columns = 15
        line_width = (base_img.width - left_padding * 2 - amount_of_columns * space_between_columns) // amount_of_columns
        line_height = 55
        for i in range(MAX_NUMBER):
            number_img = self._generate_number_image(i+1, line_width, line_height)
            paste(number_img, base_img, left, top)
            if (i+1) % amount_of_lines_by_column == 0 and i > 0:
                top = top_padding
                left += line_width + space_between_columns
            else:
                top += line_height + space_between_lines

    def _generate_number_image(self, number, width, height):
        print_number = str(number) if number > 9 else f' {number}'
        is_official_pilot = False
        pilot_name = OFFICIAL_PILOTS_NUMBERS.get(str(number))
        if not pilot_name:
            for pilot in self.config.pilots.values():
                if pilot.number == str(number):
                    pilot_name = pilot.name
                    break
        else:
            is_official_pilot = True
        fill_color = (255, 255, 255)
        stroke_color = (0, 0, 0)
        if pilot_name:
            if not is_official_pilot:
                fill_color = pilot.team.secondary_color
                stroke_color = pilot.team.main_color
            else:
                fill_color = (200, 200, 200)
                stroke_color = (150, 150, 150)

        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        font_size = 30
        number_img = text(print_number, fill_color, FontFactory.regular(font_size), 3, stroke_color, security_padding=2)
        number_pos = paste(number_img, img, left=0, use_obj=True)
        space_between = 20
        if pilot_name:
            pilot_font = FontFactory.black(self._get_pilot_font_size(pilot_name))
            name_left = number_pos.right + space_between
            if not is_official_pilot:
                pilot_img = self._get_pilot_card_img(width-name_left, height, pilot, pilot_font)
            else:
                pilot_img = Image.new('RGB', (width-name_left, height), (180,180,180))
                name_txt = text(pilot_name.upper(), (100,100,100), pilot_font)
                paste(name_txt, pilot_img, left=125)
            paste(pilot_img, img, left=name_left, with_alpha=False)
        return img

    def _get_pilot_card_img(self, width: int, height: int, pilot: Pilot, font):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        with pilot.team.get_card_image() as x:
            team_card_img = resize(x, width, height)
        # pilot name
        paste(team_card_img, img, left=0, with_alpha=False)
        name_txt = text(pilot.name.upper(), pilot.team.standing_fg, font)
        paste(name_txt, img, left=125)
        return img
