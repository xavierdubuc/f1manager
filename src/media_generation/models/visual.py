from dataclasses import dataclass
import os
from PIL import Image, ImageDraw
from .race import Race
from ..font_factory import FontFactory
from ..helpers.transform import *

@dataclass
class Visual:
    type: str
    race: Race

    @classmethod
    def get_fbrt_logo(cls, no_border=False):
        return cls._get_logo('FBRT', f'wide{"_no_border" if no_border else ""}')

    @classmethod
    def get_fbrt_round_logo(cls, color:str=None):
        color_part = f'_{color}' if color is not None else ''
        logo_name = f'round{color_part}'
        return cls._get_logo('FBRT', logo_name)

    @classmethod
    def get_fbrt_logo_50gp(cls):
        return cls._get_logo('FBRT', 'wide_50gp')

    @classmethod
    def get_f1_logo(cls, color=None):
        color_part = f'_{color}' if color is not None else ''
        return cls._get_logo('f1', f'23{color_part}')

    @classmethod
    def get_fif_logo(cls, type='round', color=None):
        color_part = f'_{color}' if color is not None else ''
        logo_name = f'{type}{color_part}'
        return cls._get_logo('fif', logo_name)

    @classmethod
    def _get_logo(cls, logo, logo_type='wide'):
        return Image.open(f'assets/logos/{logo}/{logo_type}.png')

    def get_title_image(self, width:int, height: int):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        # background

        draw = ImageDraw.Draw(img)
        line_color = (200, 0, 0)
        # ------------- \               / ------------
        #                \ ----------- /
        #   <--540--> <160> <- 645 -> <160> <--540-->
        draw.line(((0, 4), (540, 4)), fill=line_color, width=10)
        draw.line(((width-540, 4), (width, 4)), fill=line_color, width=10)
        draw.line(((538, 0), (700, 170)), fill=line_color, width=10)
        draw.line(((698, 168), (1345, 168)), fill=line_color, width=10)
        draw.line(((1343, 168), (width-538, 0)), fill=line_color, width=10)

        # FBRT logo
        left_img = Image.new('RGBA', (width//3, height), (0,0,0,0))
        with Visual.get_fbrt_round_logo(color='grey') as fbrt:
            fbrt = resize(fbrt, left_img.width // 2, int(0.8 * height))
        with Visual.get_fif_logo(type='wide', color='white') as fif:
            fif = resize(fif, left_img.width // 2, height)

        both_logo_size = fif.width + fbrt.width + 40
        both_left = -50 + (left_img.width-both_logo_size)//2
        paste(fbrt, img, left=both_left,with_alpha=False)
        paste(fif, img, left=both_left + fbrt.width + 40)

        # Title
        if self.type == 'results':
            title = self._get_race_result_title(width//3, height)
        elif self.type == 'presentation':
            title = self._get_race_presentation_title(width//3, height)
        top = height // 3
        left = (width - title.width) // 2 # centered
        img.paste(title, (left, top), title)

        # F1 23
        with Visual.get_f1_logo('white' if self.type == 'presentation' else None) as f1:
            f1.thumbnail((width//4, height), Image.Resampling.LANCZOS)
            left = (width - f1.width) - 40 # right aligned, with a small padding
            top = (height-f1.height)//2 # centered
            img.paste(f1, (left, top), f1)
        return img

    def _get_race_result_title(self, width, height):
        if len(str(self.race.round)) == 1:
            font_size = 68
        else:
            font_size = 64
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        font = FontFactory.bold(font_size)
        draw_img = ImageDraw.Draw(img)
        _, _, whole_width, _ = draw_img.textbbox((0, 0), f'Race {self.race.round} Result', font)
        _, _, race_width, _ = draw_img.textbbox((0, 0), f'Race', font)
        _, _, number_width, _ = draw_img.textbbox((0, 0), f'{self.race.round}', font)
        race_left = (width-whole_width) // 2
        number_left = race_left + race_width + 20
        fastest_left = number_left + number_width
        draw_img.text((race_left,0), 'Race', (255, 255, 255), font)
        draw_img.text((number_left,0), f'{self.race.round}', (255, 0, 0), font)
        draw_img.text((fastest_left,0), ' Result', (255, 255, 255), font)
        return img

    def _get_race_presentation_title(self, width, height):
        font_size = 68
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        font = FontFactory.bold(font_size)
        draw_img = ImageDraw.Draw(img)
        _, _, whole_width, _ = draw_img.textbbox((0, 0), f'COURSE {self.race.round}', font)
        _, _, race_width, _ = draw_img.textbbox((0, 0), f'COURSE', font)
        race_left = (width-whole_width) // 2
        number_left = race_left + race_width + 20
        draw_img.text((race_left,0), 'COURSE', (255, 255, 255), font)
        draw_img.text((number_left,0), f'{self.race.round}', (255, 0, 0), font)
        return img