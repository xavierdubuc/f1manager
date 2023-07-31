from PIL import Image
from datetime import date
from ...font_factory import FontFactory
from ...generators.presentation_generator import PresentationGenerator

from ...helpers.transform import *
import textwrap


class VRAPresentationGenerator(PresentationGenerator):
    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        return None

    def _add_content(self, final: PngImageFile):
        main_color = (255, 255, 255)
        secundary_color = (35, 235, 125)
        padding_between_blocks = 80
        padding_between_lines = 10
        font = FontFactory.get_font('Impact', 76)

        # TITLE
        first_line_title = text('CHAMPIONNAT', main_color, font)
        first_line_pos = paste(first_line_title, final, top=20)
        second_line_title = text('VIRTUAL RACING ACADEMY', main_color, font)
        second_line_pos = paste(second_line_title, final, top=first_line_pos.bottom+padding_between_lines)

        green_v = text('V', secundary_color, font)
        paste(green_v,final,second_line_pos.left, second_line_pos.top)

        green_r = text('R', secundary_color, font)
        paste(green_r,final,second_line_pos.left+260, second_line_pos.top)

        green_a = text('A', secundary_color, font)
        paste(green_a,final,second_line_pos.left+500, second_line_pos.top)

        # CIRCUIT
        race = self.config.race
        circuit = race.circuit
        with circuit.get_flag() as flag:
            flag = resize(flag, height=58)
            city = circuit.get_city_img(font)
            circuit_inner_padding = 20
            circuit_width = flag.width + city.width + circuit_inner_padding
            circuit_left = (final.width-circuit_width) // 2
            circuit_top = second_line_pos.bottom+padding_between_blocks
            flag_pos = paste(flag, final, left=circuit_left, top=circuit_top+18)
            city_pos = paste(city, final, left=flag_pos.right + circuit_inner_padding, top=circuit_top)

        # COURSE & DATE
        course = text('COURSE', main_color, font)
        course_pos = paste(course, final, top=city_pos.bottom + padding_between_blocks)
        day = race.full_date.strftime('%d')
        month = race.full_date.strftime('%m')
        date_txt = text(f'{day}/{month}', main_color, font)
        course_date_pos = paste(date_txt, final, top=course_pos.bottom+padding_between_lines)

        # MONTH & YEAR
        year = text(date.today().strftime('%Y'), main_color, font)
        month_fullname = month_fr(race.full_date.month-1).upper()
        month_and_day = text(f'{month_fullname} {day}', main_color, font)
        mandd_pos = paste(month_and_day, final, top=course_date_pos.bottom+padding_between_blocks)
        year_pos = paste(year, final, top=mandd_pos.bottom+padding_between_lines)

        # HOUR
        hour = text(race.hour, main_color, font)
        paste(hour, final, top=year_pos.bottom+padding_between_blocks)