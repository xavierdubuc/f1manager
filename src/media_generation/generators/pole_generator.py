import logging

from dataclasses import dataclass
from PIL import Image
from PIL.PngImagePlugin import PngImageFile

from src.media_generation.generators.abstract_race_generator import AbstractRaceGenerator

from ..font_factory import FontFactory
from ..helpers.transform import *
from ..models.pilot import Pilot
from ..models.visual import Visual

_logger = logging.getLogger(__name__)

@dataclass
class PoleGenerator(AbstractRaceGenerator):
    visual_type: str = 'pole'

    def _get_pole_pilot(self) -> Pilot:
        return self.race.qualification_result.rows[0].pilot

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        return None

    def _generate_basic_image(self) -> PngImageFile:
        pole_pilot = self._get_pole_pilot()
        if not pole_pilot:
            _logger.error('No pilot in pole, using default bg color')
            color = (255,255,255)
        else:
            color = pole_pilot.team.get_pole_colors()['bg']
        return Image.new('RGB', (1080, 1650), color=color)

    def _get_pilot_image(self, pilot: Pilot, width, height):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        team_pilot_img = pilot.get_long_range_image()
        img = resize(team_pilot_img, width, height)
        return img

    def _get_podium_img(self):
        first = self._get_pole_pilot()
        color = first.team.get_pole_colors()['fg']
        second = self.race.qualification_result.rows[1].pilot
        third = self.race.qualification_result.rows[2].pilot
        separator = '  /  '
        full_text = f'1st {first.name}{separator}2nd {second.name}{separator}3rd {third.name}'.upper()
        Font = FontFactory.black
        font = Font(24)
        width, height = text_size(full_text, font)
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        first_pos_img = get_ordinal_img(1, color=color, Font=Font)
        first_pos_pos = paste(first_pos_img, img, left=0)
        first_name_img = text(f'{first.name}{separator}'.upper(), color, font)
        first_name_pos = paste(first_name_img, img, first_pos_pos.right)

        second_pos_img = get_ordinal_img(2, color=color, Font=Font)
        second_pos_pos = paste(second_pos_img, img, left=first_name_pos.right)
        second_name_img = text(f'{second.name}{separator}'.upper(), color, font)
        second_name_pos = paste(second_name_img, img, second_pos_pos.right)

        third_pos_img = get_ordinal_img(3, color=color, Font=Font)
        third_pos_pos = paste(third_pos_img, img, left=second_name_pos.right)
        third_name_img = text(f'{third.name}'.upper(), color, font)
        paste(third_name_img, img, third_pos_pos.right)
        return img

    def _add_content(self, final: PngImageFile):
        pole_pilot = self._get_pole_pilot()
        if not pole_pilot:
            raise Exception('There is not pilot in pole !?')
        colors = pole_pilot.team.get_pole_colors()
        draw_lines(final, colors['line'], space_between_lines=10, line_width=2)
        repeat_text(final, (0, 0, 0, 177), pole_pilot.name.upper(), Font=FontFactory.polebg, font_size=200)

        with Visual.get_fbrt_logo(True) as logo:
            paste(resize(logo, final.width//5, final.height//5), final, left=30, top=30)
        # PILOT IMG
        pilot_img = self._get_pilot_image(pole_pilot, final.width, final.height)
        paste(pilot_img, final)

        # GRADIENT
        img_filter = Image.new('RGB', (final.width, final.height//2), colors['line'])
        gradient(img_filter, GradientDirection.DOWN_TO_UP)
        paste(img_filter, final, top=final.height//2)
        # POLE TEXT
        pole_txt_img = rotated_text('POLE', (255, 255, 255, 0), FontFactory.black(360),
                                    stroke_width=15, stroke_fill=colors['fg'], angle=15)
        paste(pole_txt_img, final, top=int(0.363 * final.height))

        # PODIUM TEXT
        podium_img = self._get_podium_img()
        paste(podium_img, final, top=final.height-60)
