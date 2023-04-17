from dataclasses import dataclass
from PIL import Image, ImageDraw

from .circuit import Circuit
from .pilot import Pilot


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
        elif self.type.startswith('Double Grid', 'Sprint (1)'):
            return 10
        return None

    def get_title_image_simple(self, width:int, height:int, date_font, circuit_font):
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        day_left = 10
        _,_,day_width,day_height = draw.textbbox((0,0), f'{self.day}.', date_font)
        _,_,month_width, month_height = draw.textbbox((0,0), self.month, date_font)
        day_top = (height-day_height) // 2
        month_top = (height-month_height) // 2
        month_left = day_left+day_width + 10

        # day
        draw.text((day_left, day_top), f'{self.day}.', 'white', date_font)
        # month
        draw.text((month_left,month_top), self.month, 'grey', date_font)

        circuit_img = self.circuit.get_title_image(height, circuit_font)
        circuit_top = (height-circuit_img.height) // 2
        circuit_left = month_left + month_width + 20
        img.paste(circuit_img, (circuit_left, circuit_top), circuit_img)
        return img

    def get_just_information_image(self, width: int, height: int, font):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        bg_top = 0
        bg = Image.new('RGB', (width, height), (80, 80, 80))
        alpha = Image.linear_gradient('L').rotate(90).resize((width, height))
        bg.putalpha(alpha)
        img.paste(bg, (0, bg_top), bg)

        draw_canvas = ImageDraw.Draw(img)
        with Image.open('assets/redcorner.png') as red_corner:
            red_corner = red_corner.convert('RGBA')
            img.paste(red_corner, (0, bg_top), red_corner)
        draw_canvas.rectangle(((0,bg_top+red_corner.height), (9, bg_top+red_corner.height+325)), fill=(255, 0, 0))
        draw_canvas.rectangle(((red_corner.width-2,bg_top), (width, bg_top+9)), fill=(255, 0, 0))

        # infos
        title_color = (238,204,81)
        info_color = (255, 255, 255)
        draw_canvas.text((50,bg_top+50), f'Longueur', title_color, font)
        draw_canvas.text((350,bg_top+50), f'Nombre de tours', title_color, font)
        draw_canvas.text((50,bg_top+100), f'{self.circuit.lap_length} Km', info_color, font)
        draw_canvas.text((350,bg_top+100), f'{self.laps} tours', info_color, font)
        draw_canvas.text((50,bg_top+175), f'Distance totale', title_color, font)
        draw_canvas.text((50,bg_top+225), f'{self.get_total_length()} Km', info_color, font)
        draw_canvas.text((50,bg_top+300), f'Meilleur temps', title_color, font)
        draw_canvas.text((50,bg_top+350), f'{self.circuit.best_lap}', info_color, font)

        # map
        with Image.open(f'assets/circuits/maps/{self.circuit.id}.png') as map:
            map.thumbnail((width, height//2), Image.Resampling.LANCZOS)
            img.paste(map, (width - map.width, height - map.height), map)
        return img

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