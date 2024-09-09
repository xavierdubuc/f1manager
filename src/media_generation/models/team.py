import logging
import os.path
from dataclasses import dataclass
from typing import Union
from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngImageFile

from src.media_generation.helpers.transform import paste, resize


ASSETS_PATH = 'assets/teams'
_logger = logging.getLogger(__name__)


@dataclass
class Team:
    name: str
    title: str
    display_name: str
    psd_name: str = None
    main_color: Union[str, tuple] = 'white'
    alternate_main_color: Union[str, tuple] = None
    secondary_color: Union[str, tuple] = 'black'
    box_color: Union[str, tuple] = 'black'
    lineup_fg_color: Union[str, tuple] = (255, 255, 255)
    lineup_bg_color: Union[str, tuple] = 'black'
    standing_bg: Union[str, tuple] = 'black'
    standing_fg: Union[str, tuple] = 'white'
    breaking_fg_color: Union[str, tuple] = (255, 255, 255)
    breaking_bg_color: Union[str, tuple] = (255, 255, 255)
    breaking_line_color: Union[str, tuple] = (0, 0, 0)
    breaking_use_white_logo: bool = False
    pole_fg_color: Union[str, tuple] = None
    pole_bg_color: Union[str, tuple] = None
    pole_line_color: Union[str, tuple] = None
    transparent_color: Union[str, tuple] = None
    card_image_path: str = None
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
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.polygon(
            ((0, height),
             (height, 0),
             (width, 0),
             (width-height, height)),
            self.lineup_bg_color
        )
        return img

    def get_box_image(self, width: int = 5, height: int = 30) -> PngImageFile:
        return Image.new('RGB', (width, height), self.box_color)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Team):
            return value.name == self.name
        if isinstance(value, str):
            return self.name == value
        return False
