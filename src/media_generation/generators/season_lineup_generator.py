import math
from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngImageFile
from ..models import Pilot, Visual
from ..helpers.transform import *
from ..generators.abstract_generator import AbstractGenerator

RESERVISTS_MODE = False

class SeasonLineupGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'season_lineup'

    def _add_content(self, base_img: PngImageFile):
        main_pilots_objects = {k:p for i, (k, p) in enumerate(self.config.pilots.items()) if i < 20 }
        reservists_objects = {k:p for i, (k, p) in enumerate(self.config.pilots.items()) if i >= 20 }
        pilots_objects = (main_pilots_objects if not RESERVISTS_MODE else reservists_objects).values()
        if self.visual_config.get('sort'):
            pilots = sorted(pilots_objects, key=lambda x: int(x.number))
        else:
            pilots = list(pilots_objects)
        amount_of_pilots = len(pilots)
        title_height = 200
        title_img = self._get_title_img(base_img.width, title_height)
        title_position = paste(title_img, base_img, top=0)

        left_padding = self.visual_config['padding']['left']
        top_padding = self.visual_config['padding']['top']

        content_height = base_img.height - title_height - 50
        padding_h = 20
        padding_v = 0
        amount_of_lines = math.ceil(amount_of_pilots / 2)
        row_height = min(85, (content_height - padding_v*amount_of_lines) // amount_of_lines)
        pilot_width = (base_img.width - 3 * padding_h)  // 2
        even_left = left_padding
        odd_left = pilot_width + 2 * padding_h
        even_top = title_position.bottom + top_padding
        odd_top = even_top + row_height // 5
        for i,pilot in enumerate(pilots):
            top = even_top if i % 2 == 0 else odd_top
            left = even_left if i % 2 == 0 else odd_left
            pilot_img = self._get_pilot_img(pilot, pilot_width, row_height)
            pilot_pos = paste(pilot_img, base_img, left=left, top=top)
            if i % 2 == 0:
                even_top = pilot_pos.bottom + padding_v
            else:
                odd_top = pilot_pos.bottom + padding_v

    def _get_title_img(self, width:int, height:int) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))

        left_logo_config = self.visual_config.get('left_logo')
        if left_logo_config:
            with Image.open(left_logo_config['path']) as left_logo:
                left_logo = resize(left_logo, height, left_logo_config['height'])
                paste(left_logo, img, left=left_logo_config['left'], top=left_logo_config['top'])

        right_logo_config = self.visual_config.get('right_logo')
        if right_logo_config:
            with Image.open(right_logo_config['path']) as right_logo:
                right_logo = resize(right_logo, height=right_logo_config['height'])
                paste(right_logo, img, left=img.width-right_logo.width, top=height-right_logo.height + right_logo_config['top'])

        font_size = self.visual_config['title'].get('font_size', 60)
        font_color = self.visual_config['title'].get('font_color', (0,0,0))
        font_name = self.visual_config['title'].get('font')
        if font_name:
            font = FontFactory.font(font_name, font_size)
        else:
            font = FontFactory.black(font_size)
        title_text = text(f'SAISON {self.season}', font_color, font)
        title2_text = text('RÉSERVISTES' if RESERVISTS_MODE else 'PILOTES', font_color, font)
        title_top = (height-(title_text.height+title2_text.height)) // 2
        title_pos = paste(title_text, img, top=title_top)
        paste(title2_text, img, top=title_pos.bottom+20)
        return img

    def _get_pilot_img(self, pilot:Pilot, width:int, height:int) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.line(((0, 0), (width, 0)), fill=(0,0,0,80), width=2)
        left_width = width // 3
        right_width = width - left_width
        left_img = Image.new('RGBA', (left_width, height), (0,0,0,0))
        right_img = Image.new('RGBA', (right_width, height), (0,0,0,0))

        number_font_config = self.visual_config['rows']['number']
        number_font_size = number_font_config.get('font_size', 65)
        number_font_name = number_font_config.get('font')
        if number_font_name:
            number_font = FontFactory.font(number_font_name, number_font_size)
        else:
            number_font = FontFactory.black(number_font_size)
        number_text = text(
            str(pilot.number or '-'),
            pilot.team.secondary_color,
            number_font,
            number_font_config['stroke_width'],
            pilot.team.main_color,
            security_padding=4
        )
        paste(number_text, left_img, top=self.visual_config['rows']['number']['top'])

        pilot_name_font_config = self.visual_config['rows']['pilot_name']
        pilot_name_font_size = pilot_name_font_config.get('font_size', 60)
        pilot_name_font_name = pilot_name_font_config.get('font')
        if pilot_name_font_name:
            pilot_name_font = FontFactory.font(pilot_name_font_name, pilot_name_font_size)
        else:
            pilot_name_font = FontFactory.bold(pilot_name_font_size)
        name_color = pilot.team.standing_fg if not pilot.reservist else (255, 255, 255)
        name_text = text(str(pilot.name.upper()), name_color, pilot_name_font)
        name_bg = Image.new('RGB', (right_width, height-20), pilot.team.main_color)
        paste(name_text, name_bg)
        paste(name_bg, right_img, left=0)

        left_position = paste(left_img, img, left=0)
        paste(right_img, img, left=left_position.right)
        return img
