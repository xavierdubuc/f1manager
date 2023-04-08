import math
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from ..helpers.transform import *
from ..generators.abstract_generator import AbstractGenerator
from ..models import Visual

class CalendarGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'calendar'

    def _get_visual_title_height(self, base_img: PngImageFile = None) -> int:
        return 355

    def _generate_basic_image(self) -> PngImageFile:
        width = 1080 
        height = 1080
        img = Image.new('RGB', (width, height), (255, 255, 255))
        draw_lines_all(img, (159, 159, 159), space_between_lines=5, line_width=1)
        return img

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        return None

    def _add_content(self, base_img: PngImageFile):
        title_width = base_img.width
        title_height = self._get_visual_title_height(base_img)
        title = self._get_title_image(title_width, title_height)
        title_position = paste(title, base_img, top=0, use_obj=True)

        left = 40
        initial_top = title_position.bottom + 20
        top = initial_top
        width = 478
        height = 100
        races = [race for race in self.config.races if race['type'] not in ('Sprint (1)', 'Double Grid (2)')]
        amount_of_races = len(races)
        halfway = math.ceil(amount_of_races / 2)
        for i, race in enumerate(races):
            race_img = self._get_race_image(race, width, height)
            race_position = paste(race_img, base_img, left, top, use_obj=True)
            if i == halfway - 1:
                left = 560
                top = initial_top
            else:
                top = race_position.bottom + 15

    def _get_race_image(self, race:dict, width: int, height: int) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        left_width = int(0.20 * width)
        right_width = width - left_width
        color = (220,0,0, 240)
        if race['type'] in ('Sprint (2)', 'Double Grid (1)', '100 %'):
            if race['type'] == 'Sprint (2)':
                type_txt = 'SPRINT'
                color = (0,200,200,240)
            elif race['type'] == 'Double Grid (1)':
                type_txt = 'DOUBLE GRID'
                color = (200, 200, 0, 240)
            else:
                type_txt = '100%'
                color = (200, 100, 200, 240)
        else:
            type_txt = None
        left_img = Image.new('RGBA', (left_width, height), color)
        right_img = Image.new('RGB', (right_width, height), (31,31,31))


        # left_part
        round_text = text(f"R{race['index']}", (255, 255, 255), FontFactory.black(36))
        paste(round_text, left_img, top=(height-round_text.height)//2-3,use_obj=True)

        if type_txt in ('SPRINT', '100%') :
            type_txt_img = text(type_txt, (255,255,255), FontFactory.regular(16))
            paste(type_txt_img, left_img, top=height-type_txt_img.height - 10)
        elif type_txt == 'DOUBLE GRID':
            type_txt_img = text('DOUBLE', (255,255,255), FontFactory.regular(16))
            paste(type_txt_img, left_img, top=10)
            type_txt_img = text('GRID', (255,255,255), FontFactory.regular(16))
            paste(type_txt_img, left_img, top=height-type_txt_img.height - 10)

        # right part
        circuit = race['circuit']
        if circuit:
            with circuit.get_flag() as circuit_flag:
                flag = resize(circuit_flag, 65, 65, keep_ratio=True)
                flag_position = paste(flag, right_img, left=15, use_obj=True)
            info_left = flag_position.right + 15
        else:
            info_left = 95

        info_top = 15
        date_txt = race['date'].strftime('%d %b').upper()
        date_img = text(date_txt, (255, 255, 255), FontFactory.regular(18))
        date_position = paste(date_img, right_img, left=info_left, top=info_top, use_obj=True)

        if circuit:
            name_img = text(circuit.name.upper(), (230,0,0), FontFactory.black(24))
            name_position = paste(name_img, right_img, left=info_left, top = date_position.bottom+4, use_obj=True)

            city_img = text(circuit.city.upper(), (255,255,255), FontFactory.black(20))
            city_position = paste(city_img, right_img, left=info_left, top = name_position.bottom+6, use_obj=True)

        # paste parts
        left_img_position = paste(left_img, img, left=0, use_obj=True)
        right_img_position = paste(right_img, img, left=left_img_position.right)
        return img

    def _get_title_image(self, width: int, height: int) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        left = 50
        color = (31, 31, 31)
        font = FontFactory.black(114)

        # logo
        with Visual.get_fbrt_logo(no_border=True) as logo_fbrt:
            logo = resize(logo_fbrt, width=width, height=100, keep_ratio=True)
            logo_position = paste(logo, img, left=left, top=35, use_obj=True)

        # "Season X"
        season_txt = text(f'SEASON {self.config.season}', color, font)
        season_position = paste(season_txt, img, left=left, top=logo_position.bottom + 5, use_obj=True)

        # "Calendar"
        calendar_txt = text('CALENDAR', color, font)
        paste(calendar_txt, img, left=left, top=season_position.bottom - 5)
        return img