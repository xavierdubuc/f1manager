import logging
from dataclasses import dataclass

from PIL import Image
from src.media_generation.generators.exceptions import IncorrectDataException
from src.media_generation.readers.race_reader_models.race import Race, RaceType

from ..helpers.transform import *

_logger = logging.getLogger(__name__)
DEFAULT_TIME = '-:--.---'


@dataclass
class RaceRenderer:
    race: Race

    def get_title(self):
        return f'RACE {self.race.round} RESULT'

    def get_circuit_and_date_img(
        self,
        width: int, height: int,
        date_config: dict,
        track_config: dict
    ):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # DATE
        date_font = FontFactory.get_font(date_config.get('font'), 40, DefaultFont=FontFactory.regular)
        month_txt = date_fr(self.race.month).upper()
        month_img = text_hi_res(month_txt, date_config['color'], date_font, date_config['width'], height//3)

        day_txt = str(self.race.day)
        day_img = text_hi_res(day_txt, date_config['color'], date_font, date_config['width'], height//3)

        date_img = Image.new('RGBA', (month_img.width, height), (0, 0, 0, 0))
        day_pos = paste(day_img, date_img, top=date_config['top'])
        month_pos = paste(month_img, date_img, top=day_pos.bottom+date_config['between'])

        paste(date_img, img, left=date_config['left'])
        full_date_width = max(day_pos.right, month_pos.right) + 20

        # FLAG
        with self.race.circuit.get_flag() as flag:
            flag = resize(flag, height, height)
            flag_pos = paste(flag, img, left=full_date_width)

        circuit_left = flag_pos.right+track_config['left']

        # CIRCUIT
        circuit_img = self.race.circuit.get_full_name_img_hi_res(
            max(0, width-circuit_left),
            height,
            track_config
        )
        paste(circuit_img, img, left=circuit_left)

        return img

    def get_type_image(
        self,
        width: int,
        height: int,
        expand_round: bool = False,
        with_txt: bool = True,
        round_font: ImageFont.FreeTypeFont = FontFactory.black(36),
        text_font: ImageFont.FreeTypeFont = FontFactory.regular(16)
    ) -> PngImageFile:
        if self.race.type in (RaceType.SPRINT_1, RaceType.SPRINT_2):
            type_txt = 'SPRINT'
            color = (0, 200, 200, 240)
        elif self.race.type in (RaceType.DOUBLE_GRID_1, RaceType.DOUBLE_GRID_2):
            type_txt = 'DOUBLE GRID'
            color = (200, 200, 0, 240)
        elif self.race.type == RaceType.FULL_LENGTH:
            type_txt = '100%'
            color = (200, 100, 200, 240)
        else:
            color = (220, 0, 0, 240)
            type_txt = None
        img = Image.new('RGBA', (width, height), color)

        # left_part
        round_text = f"{'Course ' if expand_round else 'R'}{self.race.round}"
        round_img = text(round_text, (255, 255, 255), round_font)
        paste(round_img, img, top=(height-round_img.height)//2-3)

        if with_txt:
            if type_txt in ('SPRINT', '100%'):
                type_txt_img = text(type_txt, (255, 255, 255), text_font)
                paste(type_txt_img, img, top=height-type_txt_img.height - 10)
            elif type_txt == 'DOUBLE GRID':
                type_txt_img = text('DOUBLE', (255, 255, 255), text_font)
                paste(type_txt_img, img, top=10)
                type_txt_img = text('GRID', (255, 255, 255), text_font)
                paste(type_txt_img, img, top=height-type_txt_img.height - 10)

        return img

    def get_fastest_lap_image(self, width:int, height:int, config: dict):
        bgcolor = config.get('background', (30, 30, 30, 235))
        img = Image.new('RGBA', (width, height), bgcolor)

        # FASTEST LAP IMG
        with Image.open(f'assets/fastest_lap.png') as fstst_img:
            fstst_img = resize(fstst_img, height, height)
            logo_pos = paste(fstst_img, img, left=0)

        # TEAM LOGO
        team_config = config['team']
        pilot = self.race.fastest_lap_pilot
        if not pilot:
            raise IncorrectDataException(
                f'Fastest lap pilot "{self.race.fastest_lap_pilot_name}" is unknown !')
        team = pilot.team
        with team.get_results_logo() as team_img:
            team_img = resize(team_img, int(.4*height), int(.4*height))
            team_pos = paste(team_img, img, left=logo_pos.right+team_config['left'], top=team_config['top'])

        # PILOT NAME
        pilot_config = config['pilot']
        pilot_font = FontFactory.get_font(
            pilot_config.get('font'),
            34,
            FontFactory.bold
        )
        pilot_font_color = pilot_config['font_color']
        pilot_content = self.race.fastest_lap_pilot.name.upper()
        pilot_txt = text_hi_res(pilot_content, pilot_font_color, pilot_font, pilot_config['width'], pilot_config['height'])
        pilot_pos = paste(pilot_txt, img, left=team_pos.right+pilot_config['left'], top=pilot_config['top'])

        # LAP #
        lap_config = config['lap']
        lap_font = FontFactory.get_font(
            lap_config.get('font'),
            34,
            FontFactory.regular
        )
        lap_font_color = lap_config['font_color']
        lap_txt_content = lap_config['text']
        if not self.race.fastest_lap_lap:
            _logger.warning('Fastest lap "LAP" information is not filled in !')
        lap_content = f'{lap_txt_content} {self.race.fastest_lap_lap}'
        lap_txt = text_hi_res(lap_content, lap_font_color, lap_font, lap_config['width'], lap_config['height'])
        paste(lap_txt, img, left=logo_pos.right+lap_config['left'], top=lap_config['top'])

        # LAP TIME
        time_config = config['time']
        time_font = FontFactory.get_font(
            time_config.get('font'),
            34,
            FontFactory.bold
        )
        time_font_color = time_config['font_color']
        if not self.race.fastest_lap_time or self.race.fastest_lap_time == DEFAULT_TIME:
            _logger.warning('Fastest lap "TIME" information is not filled in !')
        time_txt = text_hi_res(self.race.fastest_lap_time, time_font_color, time_font, time_config['width'], time_config['height'])
        paste(time_txt, img, left=width - (time_config['width'] + time_config['right']), top=time_config['top'])

        if self.race.fastest_lap_point_granted():
            point_config = config['point']
            point_font = FontFactory.get_font(
                point_config.get('font'),
                34,
                FontFactory.bold
            )
            point_content = f"+1 {point_config['text']}"
            point_font_color = point_config['font_color']
            point_txt = text_hi_res(point_content, point_font_color, point_font, point_config['width'], point_config['height'])
            paste(point_txt, img, left=width - (point_config['width'] + point_config['right']), top=point_config['top'])

        return img
