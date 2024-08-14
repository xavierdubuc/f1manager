
from dataclasses import dataclass
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from ..models.pilot import Pilot
from ..helpers.transform import *
from ..generators.abstract_generator import AbstractGenerator

MAX_NUMBER = 99

OFFICIAL_PILOTS_NUMBERS = {
    '1': '-',
    '2': 'Sargeant',
    '3': 'Ricciardo',
    '4': 'Norris',
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
    '55': 'Sainz',
    '63': 'Russell',
    '77': 'Bottas',
    '81': 'Piastri'
}

@dataclass
class NumbersGenerator(AbstractGenerator):
    visual_type: str = 'numbers'

    def _get_pilot_font(self, name):
        size = self.visual_config['rows']['pilot_name']['font_size']
        if len(name) >= 12:
            size = int(size - size/10)
        if len(name) >= 15:
            size = int(size - size/10)

        font_name = self.visual_config['rows']['number'].get('font')
        if font_name:
            return FontFactory.font(font_name, size)
        return FontFactory.black(size)

    def _add_content(self, base_img: PngImageFile):
        left_padding = self.visual_config['padding']['left']
        top_padding = self.visual_config['padding']['top']
        left = left_padding
        top = top_padding
        amount_of_columns = 5
        amount_of_lines_by_column = 20
        space_between_lines = self.visual_config['rows']['padding']['top']
        space_between_columns = self.visual_config['rows']['padding']['top']
        line_width = (base_img.width - left_padding * 2 - amount_of_columns * space_between_columns) // amount_of_columns
        line_height = self.visual_config['rows']['height']

        for i in range(MAX_NUMBER):
            number_img = self._generate_number_image(i+1, line_width, line_height)
            paste(number_img, base_img, left, top)
            if (i+1) % amount_of_lines_by_column == 0 and i > 0:
                top = top_padding
                left += line_width + space_between_columns
            else:
                top += line_height + space_between_lines

    def _generate_number_image(self, number, width, height):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # determining pilot name (official or not) and colors based on this
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

        number_font_size = self.visual_config['rows']['number']['font_size']
        number_font_name = self.visual_config['rows']['number'].get('font')
        if number_font_name:
            number_font = FontFactory.font(number_font_name, number_font_size)
        else:
            number_font = FontFactory.regular(number_font_size)
        number_width = self.visual_config['rows']['number']['width']
        left_img = Image.new('RGBA', (number_width, height), (0,0,0,0))
        number_img = text(str(number), fill_color, number_font, 3, stroke_color, security_padding=2)
        paste(number_img, left_img)
        number_pos = paste(left_img, img, left=0)

        # Pilot card
        space_between = 20
        if pilot_name:
            pilot_font = self._get_pilot_font(pilot_name)
            name_left = number_pos.right + space_between
            if not is_official_pilot:
                pilot_img = self._get_pilot_card_img(width-name_left, height, pilot, pilot_font)
            else:
                pilot_img = Image.new('RGB', (width-name_left, height), (180,180,180))
                name_txt = text(pilot_name.upper(), (100,100,100), pilot_font)
                left = self.visual_config['rows']['pilot_name']['left']
                paste(name_txt, pilot_img, left=left)
            paste(pilot_img, img, left=name_left, with_alpha=False)
        return img

    def _get_pilot_card_img(self, width: int, height: int, pilot: Pilot, font):
        img = Image.new('RGBA', (width, height), pilot.team.standing_bg)
        team_card_img = pilot.team.build_card_image(width, height)
        # pilot name
        paste(team_card_img, img, left=0, with_alpha=False)
        name_txt = text(pilot.name.upper(), pilot.team.standing_fg, font)
        left = self.visual_config['rows']['pilot_name']['left']
        paste(name_txt, img, left=left)
        return img
