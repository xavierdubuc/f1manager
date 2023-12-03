from dataclasses import dataclass
from PIL import Image

from src.media_generation.readers.race_reader_models.race import Race, RaceType
from .pilot import Pilot
from ..helpers.transform import *


@dataclass
class RaceRenderer:
    race: Race

    def get_title(self):
        return f'RACE {self.race.round} RESULT'

    def get_circuit_and_date_img(
        self,
        width: int, height: int,
        name_font=FontFactory.black(24),
        city_font=FontFactory.black(20),
        date_font=FontFactory.regular(18),
        name_color=(230, 0, 0),
        city_color=(255, 255, 255),
        date_color=(255, 255, 255)
    ):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # DATE
        month_txt = date_fr(self.race.month).upper()
        month_img = text(month_txt, date_color, date_font)

        day_txt = str(self.race.day)
        day_img = text(day_txt, date_color, date_font)

        date_img = Image.new(
            'RGBA',
            (month_img.width, month_img.height+day_img.height+10),
            (0, 0, 0, 0)
        )
        day_pos = paste(day_img, date_img, top=0)
        month_pos = paste(month_img, date_img, top=day_pos.bottom+10)

        paste(date_img, img, left=0)
        full_date_width = max(day_pos.right, month_pos.right) + 20

        # FLAG
        with self.race.circuit.get_flag() as flag:
            flag = resize(flag, height, height)
            flag_pos = paste(flag, img, left=full_date_width)

        circuit_left = flag_pos.right+20

        # CIRCUIT
        circuit_img = self.race.circuit.get_full_name_img(
            max(0,width-circuit_left),
            height,
            name_font=name_font,
            city_font=city_font,
            name_color=name_color,
            city_color=city_color
        )
        paste(circuit_img, img, left=circuit_left)

        return img

    def get_type_image(
        self,
        width: int,
        height: int,
        expand_round: bool = False,
        round_font: ImageFont.FreeTypeFont = FontFactory.black(36),
        text_font: ImageFont.FreeTypeFont = FontFactory.regular(16)
    ) -> PngImageFile:
        if self.race.type == RaceType.SPRINT_2:
            type_txt = 'SPRINT'
            color = (0,200,200,240)
        elif self.race.type == RaceType.DOUBLE_GRID_1:
            type_txt = 'DOUBLE GRID'
            color = (200, 200, 0, 240)
        elif self.race.type == RaceType.FULL_LENGTH:
            type_txt = '100%'
            color = (200, 100, 200, 240)
        else:
            color = (220,0,0, 240)
            type_txt = None
        img = Image.new('RGBA', (width, height), color)

        # left_part
        round_text = f"{'Course ' if expand_round else 'R'}{self.race.round}"
        round_img = text(round_text, (255, 255, 255), round_font)
        paste(round_img, img, top=(height-round_img.height)//2-3)

        if type_txt in ('SPRINT', '100%') :
            type_txt_img = text(type_txt, (255,255,255), text_font)
            paste(type_txt_img, img, top=height-type_txt_img.height - 10)
        elif type_txt == 'DOUBLE GRID':
            type_txt_img = text('DOUBLE', (255,255,255), text_font)
            paste(type_txt_img, img, top=10)
            type_txt_img = text('GRID', (255,255,255), text_font)
            paste(type_txt_img, img, top=height-type_txt_img.height - 10)

        return img
