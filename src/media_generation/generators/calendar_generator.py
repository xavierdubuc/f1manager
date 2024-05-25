import math
from typing import List
from PIL import Image
from PIL.PngImagePlugin import PngImageFile

from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.models.race_renderer import RaceRenderer
from src.media_generation.readers.race_reader_models.race import Race, RaceType
from ..helpers.transform import *
from ..generators.abstract_generator import AbstractGenerator
from ..models import Visual

class CalendarGenerator(AbstractGenerator):
    def __init__(self, championship_config: dict, config: GeneratorConfig, season: int, identifier: str = None, *args, **kwargs):
        super().__init__(championship_config, config, season, identifier, *args, **kwargs)
        self.races: List[Race] = self.config.races

    def _get_visual_type(self) -> str:
        return 'calendar'

    def _get_visual_title_height(self, base_img: PngImageFile = None) -> int:
        return 355 # FIXME use custom title mechanism

    def _add_content(self, base_img: PngImageFile):
        title_width = base_img.width
        title_height = self._get_visual_title_height(base_img)
        title = self._get_title_image(title_width, title_height)
        title_position = paste(title, base_img, top=0)

        left = 40
        initial_top = title_position.bottom + 20
        top = initial_top
        width = 478
        height = 100
        races = [
            race for race in self.races
            if race.type not in (RaceType.SPRINT_1, RaceType.DOUBLE_GRID_2)
        ]
        amount_of_races = len(races)
        halfway = math.ceil(amount_of_races / 2)
        for i, race in enumerate(races):
            race_img = self._get_race_image(race, width, height)
            race_position = paste(race_img, base_img, left, top)
            if i == halfway - 1:
                left = 560
                top = initial_top
            else:
                top = race_position.bottom + 15

    def _get_race_image(self, race:Race, width: int, height: int) -> PngImageFile:
        race_renderer = RaceRenderer(race)
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        left_width = int(0.20 * width)
        right_width = width - left_width

        # left_part
        left_img = race_renderer.get_type_image(left_width, height)

        # right part
        right_img = Image.new('RGB', (right_width, height), (31,31,31))
        circuit = race.circuit
        if circuit:
            with circuit.get_flag() as circuit_flag:
                flag = resize(circuit_flag, 65, 65, keep_ratio=True)
                flag_position = paste(flag, right_img, left=15)
            info_left = flag_position.right + 15
        else:
            info_left = 95

        info_top = 15
        date_txt = race.full_date.strftime('%d %b').upper() # FIXME french it up
        date_img = text(date_txt, (255, 255, 255), FontFactory.regular(18))
        date_position = paste(date_img, right_img, left=info_left, top=info_top)

        if circuit:
            circuit_img = circuit.get_full_name_img(right_width, height-date_position.bottom-8)
            paste(circuit_img, right_img, left=info_left, top = date_position.bottom)

        # paste parts
        left_img_position = paste(left_img, img, left=0)
        paste(right_img, img, left=left_img_position.right)
        return img

    def _get_title_image(self, width: int, height: int) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        left = 50
        color = (31, 31, 31)
        font = FontFactory.black(100)

        # logo
        top = 10
        with Visual.get_fbrt_round_logo() as logo_fbrt:
            logo = resize(logo_fbrt, height=150)
            logo_position = paste(logo, img, left=left, top=top)

        with Visual.get_fif_logo('wide') as fif_logo_img:
            fif_logo_img = resize(fif_logo_img, height=80)
            paste(fif_logo_img, img, top=height-fif_logo_img.height,  left=width - fif_logo_img.width - 10)

        # "Season X"
        season_txt = text(f'SAISON {self.config.season}', color, font)
        season_position = paste(season_txt, img, left=left, top=logo_position.bottom + 5)

        # "Calendar"
        calendar_txt = text('CALENDRIER', color, font)
        paste(calendar_txt, img, left=left, top=season_position.bottom - 5)
        return img
