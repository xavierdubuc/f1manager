import math
from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngImageFile
from ..models import Pilot, Visual
from ..helpers.transform import *
from ..generators.abstract_generator import AbstractGenerator

RESERVISTS_MODE = False

class SeasonLineupGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'season_lineup'

    def _get_visual_title_height(self, base_img: PngImageFile = None) -> int:
        return 200

    def _generate_basic_image(self) -> PngImageFile:
        width = 1080
        height = 1080
        img = Image.new('RGB', (width, height), (255, 255, 255))
        # draw_lines_all(img, (159,159,159), space_between_lines=6, line_width=1)
        return img

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        return None

    def _add_content(self, base_img: PngImageFile):
        pilots = {k:p for i, (k, p) in enumerate(self.config.pilots.items()) if i < 20 }
        reservists = {k:p for i, (k, p) in enumerate(self.config.pilots.items()) if i >= 20 }
        # pilots = sorted(pilots.values(), key=lambda x: int(x.number))
        pilots = list((reservists if RESERVISTS_MODE else pilots).values())
        amount_of_pilots = len(pilots)
        title_height = self._get_visual_title_height()
        title_img = self._get_title_img(base_img.width, title_height)
        title_position = paste(title_img, base_img, top=0, use_obj=True)
        padding_h = 20
        content_height = base_img.height - title_height - 50
        padding_v = 0
        amount_of_lines = math.ceil(amount_of_pilots / 2)
        pilot_height = min(85, (content_height - padding_v*amount_of_lines) // amount_of_lines)
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
        with Visual.get_fbrt_round_logo() as logo:
            fbrt_logo = resize(logo, height, height-10)
            paste(fbrt_logo, img, left=80, top=10, use_obj=True)
        with Visual.get_fif_logo('wide') as logo:
            logo = resize(logo, height=int(0.5*img.height))
            paste(logo, img, left=img.width-logo.width, top=height-logo.height+10)
        title_text = text(f'SEASON {self.season}', (0,0,0), FontFactory.black(60))
        title2_text = text('RESERVISTS' if RESERVISTS_MODE else 'DRIVERS', (0,0,0), FontFactory.black(60))
        title_top = (height-(title_text.height+title2_text.height)) // 2
        title_pos = paste(title_text, img, top=title_top, use_obj=True)
        paste(title2_text, img, top=title_pos.bottom+20)
        return img

    def _get_pilot_img(self, pilot:Pilot, width:int, height:int) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.line(((0, 0), (width, 0)), fill=(0,0,0,80), width=2)
        left_width = width // 3
        right_width = width - left_width
        left_img = Image.new('RGBA', (left_width, height), (0,0,0,0))
        right_img = Image.new('RGBA', (right_width, height), (0,0,0,0))

        number_text = text(str(pilot.number or '-'), pilot.team.secondary_color, FontFactory.black(65), 4, pilot.team.main_color, security_padding=4)
        paste(number_text, left_img)

        name_color = pilot.team.standing_fg if not pilot.reservist else (255, 255, 255)
        name_text = text(str(pilot.name.upper()), name_color, FontFactory.bold(25))
        name_bg = Image.new('RGB', (right_width, height-20), pilot.team.main_color)
        paste(name_text, name_bg)
        paste(name_bg, right_img, left=0)

        left_position = paste(left_img, img, left=0, use_obj=True)
        paste(right_img, img, left=left_position.right)
        return img