from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from ..models import Pilot
from ..helpers.transform import *
from ..generators.abstract_generator import AbstractGenerator

MAX_NUMBER = 99

OFFICIAL_PILOTS_NUMBERS = {
    '1': '-',
    '3': 'Ricciardo',
    '4': 'Norris',
    '5': 'Vettel',
    '6': 'Latifi',
    '10': 'Gasly',
    '11': 'Perez',
    '14': 'Alonso',
    '16': 'Leclerc',
    '17': '/',
    '18': 'Stroll',
    '20': 'Magnussen',
    '22': 'Tsunoda',
    '23': 'Albon',
    '24': 'Zhou',
    '27': 'Hulkenberg',
    '31': 'Ocon',
    '33': 'Verstappen',
    '44': 'Hamilton',
    '47': 'Schumacher',
    '55': 'Sainz',
    '63': 'Russell',
    '77': 'Bottas',

}


class NumbersGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'numbers'

    def _get_visual_title_height(self, base_img: PngImageFile = None) -> int:
        return 200

    def _generate_basic_image(self) -> PngImageFile:
        width = (1080 * 2) + 60
        height = 1440
        img = Image.new('RGB', (width, height), (255, 255, 255))
        draw_lines_all(img, (159, 159, 159), space_between_lines=10, line_width=2)
        return img

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        return None

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
        pilot_font = FontFactory.black(20)
        if pilot_name:
            name_left = number_pos.right + space_between
            if not is_official_pilot:
                pilot_img = self._get_pilot_card_img(width-name_left, height, pilot, pilot_font)
            else:
                pilot_img = Image.new('RGB', (width-name_left, height), (150,150,150))
                name_txt = text(pilot_name.upper(), (100,100,100), pilot_font)
                paste(name_txt, pilot_img, left=125)
            paste(pilot_img, img, left=name_left, with_alpha=False)
        return img

    def _get_pilot_card_img(self, width: int, height: int, pilot: Pilot, font):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        with Image.open(f'assets/teams/empty_cards/{pilot.team.name}.png') as i:
            team_card_img = resize(i.copy(), width, height)
        # pilot name
        paste(team_card_img, img, left=0, with_alpha=False)
        name_txt = text(pilot.name.upper(), pilot.team.standing_fg, font)
        paste(name_txt, img, left=125)
        return img
