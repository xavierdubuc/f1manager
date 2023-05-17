from dataclasses import dataclass
from PIL import Image, ImageDraw

from src.media_generation.font_factory import FontFactory

from .circuit import Circuit
from .pilot import Pilot
from ..helpers.transform import *


@dataclass
class Race:
    round: int
    laps: int
    day: str
    month: str
    hour: str
    circuit: Circuit
    pilots: dict
    teams: list
    type: str
    swappings: dict = None

    def get_total_length(self):
        return '{:.3f}'.format(self.laps * self.circuit.lap_length)

    def get_title(self):
        return f'RACE {self.round} RESULT'

    def get_max_position_for_fastest_lap(self):
        if self.type in ('Normale', 'Sprint (2)', '100 %'):
            return 14
        elif self.type.startswith('Double Grid') or self.type.startswith('Sprint (1)'):
            return 10
        return None

    def get_pilots(self, team):
        main_pilots = [pilot for pilot in self.pilots.values() if pilot.team == team]
        if not self.swappings or len(self.swappings) == 0:
            return main_pilots
        else:
            out = []
            for pilot in main_pilots:
                pilot_to_append = pilot
                for replace_name, replaced_pilot in self.swappings.items():
                    if replaced_pilot == pilot:
                        pilot_to_append = Pilot(name=replace_name, team=team)
                        break
                out.append(pilot_to_append)
            return out

    def get_pilot(self, pilot_name:str) -> Pilot:
        pilot = self.pilots.get(pilot_name, None)
        if not pilot or pilot.reservist:
            replaces = self.swappings.get(pilot_name)
            if not replaces:
                return None
            team = replaces.team
            pilot = Pilot(name=pilot_name, team=team)
        return pilot

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
        month_txt = date_fr(self.month).upper()
        month_img = text(month_txt, date_color, date_font)

        day_txt = str(self.day)
        day_img = text(day_txt, date_color, date_font)

        date_img = Image.new(
            'RGBA',
            (month_img.width, month_img.height+day_img.height+10),
            (0, 0, 0, 0)
        )
        day_pos = paste(day_img, date_img, top=0, use_obj=True)
        month_pos = paste(month_img, date_img, top=day_pos.bottom+10, use_obj=True)

        paste(date_img, img, left=0)
        full_date_width = max(day_pos.right, month_pos.right) + 20

        # FLAG
        with self.circuit.get_flag() as flag:
            flag = resize(flag, height, height)
            flag_pos = paste(flag, img, left=full_date_width, use_obj=True)

        circuit_left = flag_pos.right+20

        # CIRCUIT
        circuit_img = self.circuit.get_full_name_img(
            width-circuit_left,
            height,
            name_font=name_font,
            city_font=city_font,
            name_color=name_color,
            city_color=city_color
        )
        paste(circuit_img, img, left=circuit_left)
        
        return img