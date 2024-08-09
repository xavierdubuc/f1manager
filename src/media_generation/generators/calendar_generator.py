from typing import List

from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.models.circuit import Circuit
from src.media_generation.models.race_renderer import RaceRenderer
from src.media_generation.readers.race_reader_models.race import Race, RaceType

from ..generators.abstract_generator import AbstractGenerator
from ..helpers.transform import *


class CalendarGenerator(AbstractGenerator):
    def __init__(self, championship_config: dict, config: GeneratorConfig, season: int, identifier: str = None, *args, **kwargs):
        super().__init__(championship_config, config, season, identifier, *args, **kwargs)
        self.races: List[Race] = self.config.races

    def _get_visual_type(self) -> str:
        return 'calendar'

    def _add_content(self, base_img: PngImageFile):
        self._render_title(base_img)
        self._render_body(base_img)

    def _render_title(self, base_img: PngImageFile):
        for logo_config in self.visual_config.get('logos'):
            with Image.open(logo_config['path']) as logo_img:
                logo_width = logo_config.get('width', 100)
                logo_height = logo_config.get('height', 100)
                logo_img = resize(logo_img, height=logo_height, width=logo_width)
                self.paste_image(logo_img, base_img, logo_config)

        for title_config in self.visual_config.get('titles'):
            content = title_config.get('content', "{season}").format(season=self.season)
            title_img = self.text(title_config, content, default_font=FontFactory.black)
            self.paste_image(title_img, base_img, title_config)

    def _render_body(self, base_img: PngImageFile):
        config = self.visual_config.get('body')
        w = config.get('width', base_img.width)
        h = config.get('height', base_img.height)
        img = Image.new('RGBA', (w, h), config.get('background', (0, 0, 0, 0)))
        races = [
            race for race in self.races
            if race.type not in (RaceType.SPRINT_1, RaceType.DOUBLE_GRID_2)
        ]
        for race in races:
            self._render_race(race, len(races), img)

        self.paste_image(img, base_img, config)

    def _render_race(self, race: Race, amount_of_races: int, base_img: PngImageFile):
        config = self.visual_config.get('race')
        w = config.get('width')
        h = config.get('height')
        space_between = config.get('space_between')
        bg = config.get('background', (255, 255, 255, 255))
        img = Image.new('RGBA', (w, h), bg)

        # RACE ROUND
        race_renderer = RaceRenderer(race)
        round_config = config.get('round', {})
        round_img = race_renderer.get_race_type_image(round_config)  # FIXME badly rendered
        self.paste_image(round_img, img, round_config)

        # RACE CIRCUIT
        circuit = race.circuit
        if circuit:
            # - FLAG
            flag_config = config.get('flag', {})
            flag_w = flag_config.get('width')
            flag_h = flag_config.get('height')
            with circuit.get_flag() as circuit_flag:
                flag = resize(circuit_flag, flag_w, flag_h)
                self.paste_image(flag, img, flag_config)

        if not circuit:
            circuit = Circuit("?", "?", 0.0, "?", "?")
        # - COUNTRY & CITY
        countcity_config = config.get('countcity', {})
        countcity_w = countcity_config.get('width')
        countcity_h = countcity_config.get('height')
        countcity_img = circuit.get_full_name_img_hi_res(
            countcity_w, countcity_h, countcity_config.get('track'), use_background=bg
        )
        self.paste_image(countcity_img, img, countcity_config)

        # RACE DATE
        date_content = race.full_date.strftime('%d %b').upper()  # FIXME french it up
        date_config = config.get('date', {})
        date_font = FontFactory.get_font(date_config.get('font'), 50, FontFactory.regular)
        date_color = date_config.get('color', (0, 0, 0))
        date_w = date_config.get('width', w)
        date_h = date_config.get('height', h)
        date_img = text_hi_res(date_content, date_color, date_font, date_w, date_h, use_background=bg)
        self.paste_image(date_img, img, date_config)

        # paste
        lefts = config.get('left', [0, 540])
        halfway = amount_of_races // 2
        round = int(race.round)
        if round <= halfway:
            row = round - 1
            left = lefts[0]
        else:
            row = (round - halfway) - 1
            left = lefts[1]

        if round == 1:
            top = 0
        else:
            top = row * (h + space_between)

        paste(img, base_img, left=left, top=top)
