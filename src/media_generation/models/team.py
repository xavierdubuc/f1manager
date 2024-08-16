import logging
import os.path
from dataclasses import dataclass
from typing import List, Union
from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngImageFile

from ..font_factory import FontFactory
from ..helpers.transform import *


ASSETS_PATH = 'assets/teams'
_logger = logging.getLogger(__name__)

@dataclass
class Team:
    name: str
    title: str
    display_name: str
    psd_name:str = None
    main_color: Union[str,tuple] = 'white'
    alternate_main_color: Union[str,tuple] = None
    secondary_color: Union[str,tuple] = 'black'
    box_color: Union[str,tuple] = 'black'
    lineup_fg_color: Union[str,tuple] = (255,255,255)
    lineup_bg_color: Union[str,tuple] = 'black'
    standing_bg: Union[str,tuple] = 'black'
    standing_fg: Union[str,tuple] = 'white'
    breaking_fg_color: Union[str,tuple] = (255, 255, 255)
    breaking_bg_color: Union[str,tuple] = (255, 255, 255)
    breaking_line_color: Union[str,tuple] = (0, 0, 0)
    breaking_use_white_logo: bool = False
    pole_fg_color: Union[str,tuple] = None
    pole_bg_color: Union[str,tuple] = None
    pole_line_color: Union[str,tuple] = None
    transparent_color: Union[str,tuple] = None
    card_image_path: str= None
    driver_of_the_day_hsv_offset: int = None
    driver_of_the_day_use_grayscale: bool = False

    def __post_init__(self):
        if not self.alternate_main_color:
            self.alternate_main_color = self.standing_bg

    def get_card_image(self):
        basepath = os.path.join(ASSETS_PATH, 'empty_cards')
        if self.card_image_path:
            path = os.path.join(basepath, self.card_image_path)
        else:
            path = os.path.join(basepath, f'{self.name}.png')
        return Image.open(path)

    def build_card_image(self, width, height):
        basepath = os.path.join(ASSETS_PATH, 'card_logos')
        if self.card_image_path:
            path = os.path.join(basepath, self.card_image_path)
        else:
            path = os.path.join(basepath, f'{self.name}.png')

        img = Image.new('RGB', (width, height), self.standing_bg)
        with Image.open(path) as card_logo:
            card_logo = resize(card_logo, height=height)
        paste(card_logo, img, left=0, with_alpha=False)
        return img

    def render_logo(self, width, height, logo_height=None):
        logo_height = logo_height or height
        img = Image.new('RGB', (width, height), self.standing_bg)
        with self.get_ranking_logo() as card_logo:
            card_logo = resize(card_logo, height=logo_height)
        paste(card_logo, img)
        return img

    def get_pole_colors(self):
        return {
            'fg': self.pole_fg_color if self.pole_fg_color else self.breaking_fg_color,
            'bg': self.pole_bg_color if self.pole_bg_color else self.breaking_bg_color,
            'line': self.pole_line_color if self.pole_line_color else self.breaking_line_color
        }

    def get_ranking_logo(self):
        return Image.open(self.get_ranking_logo_path())

    def get_ranking_logo_path(self):
        if self.name in ('KickSauber', 'RedBull'):
            return self._get_alt_logo_path()
        if self.name in ('AstonMartin', 'Williams', 'McLaren', 'Alpine'):
            return self._get_white_logo_path()
        return self.get_image()

    def get_results_logo(self):
        if self.name in ('VCARB',):
            return Image.open(self._get_alt_logo_path())
        return Image.open(self.get_image())

    def get_lineup_logo_path(self):
        if self.name in ('Alpine', 'AlfaRomeo', 'VCARB', 'RedBull', 'AstonMartin', 'Ferrari', 'McLaren'):
            return self._get_alt_logo_path()
        return self.get_image()

    def get_lineup_logo(self):
        return Image.open(self.get_lineup_logo_path())

    def get_image(self):
        return os.path.join(ASSETS_PATH, f'{self.name}.png')

    def get_breaking_logo(self):
        return self._get_white_logo_path() if self.breaking_use_white_logo else self.get_image()

    def _get_white_logo_path(self):
        return os.path.join(ASSETS_PATH, f'white/{self.name}.png')

    def _get_alt_logo_path(self):
        return os.path.join(ASSETS_PATH, f'alt/{self.name}.png')

    def get_parallelogram(self, width, height):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.polygon(
            ((0, height),
            (height, 0),
            (width, 0),
            (width-height, height)),
            self.lineup_bg_color
        )
        return img

    def get_lineup_image(self, width, height, pilots:List["Pilot"]):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # Parallelogram
        parallelogram_bottom_margin = 5
        parallelogram_height = int(.32 * height) # should be ~ 67
        parallelogram_img = self.get_parallelogram(width, parallelogram_height)
        parallelogram_pos = paste(
            parallelogram_img,
            img,
            top=height-parallelogram_height - parallelogram_bottom_margin
        )

        remaining_height = height - parallelogram_height - parallelogram_bottom_margin
        max_logo_width = int(.3 * width) # ~240
        max_logo_height = int(.675 * remaining_height) # ~96
        # Logo
        with self.get_lineup_logo() as logo_img:
            logo_img = resize(logo_img, max_logo_width, max_logo_height)
            if logo_img.mode != 'RGBA':
                logo_img = logo_img.convert('RGBA')
            logo_pos = paste(logo_img, img, top=(remaining_height-max_logo_height)//2)

        # FIXME refactor below + try to open only once the psd

        pilots = [p for p in pilots if p.name != '/']
        ########
        # Pilots
        ########

        if len(pilots) == 0:
            _logger.warning(f'Team {self.name} has no pilots !')
            return img

        max_pilot_name_length = max([len(p.name) for p in pilots])
        has_long_pseudo =  max_pilot_name_length >= 15
        pilot_font = FontFactory.black(24 if has_long_pseudo else 30)
        h_padding = 10

        # PILOT #1
        left_pilot_img = self._get_lineup_pilot_image(pilots[0], pilot_font, width // 2, height, remaining_height, has_long_pseudo, text_left_padding=5)
        paste(left_pilot_img, img, top=0, left=h_padding)

        if len(pilots) == 1:
            _logger.warning(f'Team {self.name} has only one pilot !')
            return img

        # PILOT #2
        right_pilot_img = self._get_lineup_pilot_image(pilots[1], pilot_font, width // 2, height, remaining_height, has_long_pseudo)
        right_pilot_img_left = width - right_pilot_img.width - h_padding
        paste(right_pilot_img, img, top=0, left=right_pilot_img_left)

        return img

    def get_box_image(self, width:int=5, height:int=30) ->PngImageFile:
        return Image.new('RGB', (width, height), self.box_color)

    def _get_lineup_pilot_image(self, pilot:"Pilot", font: ImageFont.FreeTypeFont, width:int, height:int, img_height:int, has_long_pseudo:bool=False, text_left_padding:int=0):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        pilot_name_img = pilot.get_name_image(font, color=(255,255,255))
        vertical_shift = 26
        if not has_long_pseudo and '_' in pilot.name:
            vertical_shift = 21
        pilot_name_top = height - pilot_name_img.height - vertical_shift
        pilot_name_left = int((width-pilot_name_img.width) / 2 + text_left_padding)
        paste(pilot_name_img, img, top=pilot_name_top, left=pilot_name_left)

        # img
        pilot_img = pilot.get_close_up_image(height=img_height)
        paste(pilot_img, img, top=0)

        return img

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Team):
            return value.name == self.name
        if isinstance(value, str):
            return self.name == value
        return False
