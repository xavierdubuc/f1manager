import math
from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngImageFile
from ..models import Pilot, Visual
from ..helpers.transform import *
from ..generators.abstract_generator import AbstractGenerator

SEASON = 5

class SeasonLineupGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'season_lineup'

    def _get_visual_title_height(self, base_img: PngImageFile = None) -> int:
        return 150

    def _generate_basic_image(self) -> PngImageFile:
        width = 1080
        height = 1080
        img = Image.new('RGB', (width, height), (255, 255, 255))
        draw_lines_all(img, (159,159,159), space_between_lines=6, line_width=1)
        return img

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        return None

    def _add_content(self, base_img: PngImageFile):
        pilots = {k:p for i, (k, p) in enumerate(self.config.pilots.items()) if i < 20}
        # pilots = sorted(pilots.values(), key=lambda x: int(x.number))
        pilots = list(pilots.values())
        amount_of_pilots = len(pilots)
        title_height = self._get_visual_title_height()
        title_img = self._get_title_img(base_img.width, title_height)
        title_position = paste(title_img, base_img, top=0, use_obj=True)
        padding_h = 20
        content_height = base_img.height - title_height - 50
        padding_v = 0
        amount_of_lines = math.ceil(amount_of_pilots / 2)
        pilot_height = (content_height - padding_v*amount_of_lines) // amount_of_lines
        pilot_width = (base_img.width - 3 * padding_h)  // 2
        even_left = padding_h
        odd_left = pilot_width + 2 * padding_h
        even_top = title_position.bottom + 30
        odd_top = even_top + pilot_height // 5
        for i,pilot in enumerate(pilots):
            top = even_top if i % 2 == 0 else odd_top
            left = even_left if i % 2 == 0 else odd_left
            pilot_img = self._get_pilot_img(pilot, pilot_width, pilot_height)
            pilot_pos = paste(pilot_img, base_img, left=left, top=top, use_obj=True)
            if i % 2 == 0:
                even_top = pilot_pos.bottom + padding_v
            else:
                odd_top = pilot_pos.bottom + padding_v

    def _get_title_img(self, width:int, height:int) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        with Visual.get_fbrt_logo(no_border=True) as logo:
            fbrt_logo = resize(logo, height, height)
            logo_position = paste(fbrt_logo, img, top=20, use_obj=True)
        title_text = text(f'SEASON {SEASON} DRIVERS', (0,0,0), FontFactory.black(60))
        paste(title_text, img, top=logo_position.bottom + 10)
        return img

    def _get_pilot_img(self, pilot:Pilot, width:int, height:int) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.line(((0, 0), (width, 0)), fill=(0,0,0,80), width=2)
        left_width = width // 3
        right_width = width - left_width
        left_img = Image.new('RGBA', (left_width, height), (0,0,0,0))
        right_img = Image.new('RGBA', (right_width, height), (0,0,0,0))

        number_text = text(str(pilot.number or 'Re'), pilot.team.secondary_color, FontFactory.black(70), 4, pilot.team.main_color, security_padding=2)
        paste(number_text, left_img)

        name_text = text(str(pilot.name), pilot.team.standing_fg, FontFactory.bold(25))
        name_bg = Image.new('RGB', (right_width, height-20), pilot.team.main_color)
        paste(name_text, name_bg)
        paste(name_bg, right_img, left=0)

        left_position = paste(left_img, img, left=0, use_obj=True)
        paste(right_img, img, left=left_position.right)
        return img