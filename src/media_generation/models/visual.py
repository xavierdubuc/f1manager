from dataclasses import dataclass
from PIL import Image, ImageDraw
from .race import Race
from ..font_factory import FontFactory
from ..helpers.transform import *

@dataclass
class Visual:
    type: str
    race: Race

    @staticmethod
    def get_fbrt_logo(no_border=False):
        return Image.open(f'assets/fbrt{"_no_border" if no_border else ""}.png')

    @staticmethod
    def get_fbrt_logo_50gp():
        return Image.open(f'assets/fbrt50gp.png')

    @staticmethod
    def get_f1_logo(black=False):
        return Image.open(f'assets/f122{"_white" if black else ""}.png')

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
        with Visual.get_fbrt_logo_50gp() as fbrt:
            fbrt.thumbnail((width//3, height), Image.Resampling.LANCZOS)
            left = (width//3 - fbrt.width) // 2 # centered in the left cell
            top = (height-fbrt.height)//2 # centered
            img.paste(fbrt, (left, top), fbrt)

        # Title
        if self.type == 'details':
            title = self._get_race_result_title(width//3, height)
        elif self.type == 'fastest':
            title = self._get_race_fastest_title(width//3, height)
        elif self.type == 'lineups':
            title = self._get_race_lineup_title(width//3, height)
        elif self.type == 'presentation':
            title = self._get_race_presentation_title(width//3, height)
        top = height // 3
        left = (width - title.width) // 2 # centered
        img.paste(title, (left, top), title)

        # F1 22
        with Visual.get_f1_logo(self.type == 'presentation') as f122:
            f122.thumbnail((width//4, height), Image.Resampling.LANCZOS)
            left = (width - f122.width) - 40 # right aligned, with a small padding
            top = (height-f122.height)//2 # centered
            img.paste(f122, (left, top), f122)
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

    def _get_race_lineup_title(self, width, height):
        if len(str(self.race.round)) == 1:
            font_size = 68
            padding_right = 60
        else:
            font_size = 64
            padding_right = 90
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        font = FontFactory.bold(font_size)
        draw_img = ImageDraw.Draw(img)
        draw_img.text((0,0), 'LINE UP - RACE', (255, 255, 255), font)
        draw_img.text((width-padding_right,0), f'{self.race.round}', (255, 0, 0), font)
        return img

    def _get_race_presentation_title(self, width, height):
        font_size = 68
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        font = FontFactory.bold(font_size)
        draw_img = ImageDraw.Draw(img)
        _, _, whole_width, _ = draw_img.textbbox((0, 0), f'RACE {self.race.round}', font)
        _, _, race_width, _ = draw_img.textbbox((0, 0), f'RACE', font)
        race_left = (width-whole_width) // 2
        number_left = race_left + race_width + 20
        draw_img.text((race_left,0), 'RACE', (255, 255, 255), font)
        draw_img.text((number_left,0), f'{self.race.round}', (255, 0, 0), font)
        return img

    def _get_race_fastest_title(self, width, height):
        font_size = 60 if len(self.race.round) < 2 else 52
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        font = FontFactory.bold(font_size)
        draw_img = ImageDraw.Draw(img)
        _, _, whole_width, _ = draw_img.textbbox((0, 0), f'Race {self.race.round} - Fastest lap', font)
        _, _, race_width, _ = draw_img.textbbox((0, 0), f'Race', font)
        _, _, number_width, _ = draw_img.textbbox((0, 0), f'{self.race.round}', font)
        race_left = (width-whole_width) // 2
        number_left = race_left + race_width + 20
        fastest_left = number_left + number_width
        draw_img.text((race_left,0), 'Race', (255, 255, 255), font)
        draw_img.text((number_left,0), f'{self.race.round}', (255, 0, 0), font)
        draw_img.text((fastest_left,0), ' - Fastest lap', (255, 255, 255), font)
        return img