import logging
import os
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from src.media_generation.models.pilot import Pilot

from src.media_generation.models.visual import Visual
from ..generators.abstract_generator import AbstractGenerator
from ..helpers.transform import *

_logger = logging.getLogger(__name__)

class PilotGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'pilot'

    def _generate_basic_image(self) -> PngImageFile:
        return Image.new('RGBA', (364, 210), (0,0,0,0))

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        return None

    def _add_content(self, base_img: PngImageFile):
        if self.identifier in ('all', 'main'):
            i = 0
            path = os.path.dirname(self.config.output)
            for key, pilot in self.config.pilots.items():
                if self.identifier == 'all' or not pilot.reservist:
                    img = self._get_pilot_img(pilot, base_img.width, base_img.height)
                    if i > 0:
                        filename = os.path.join(path, f'{key}.png')
                        img.save(filename, quality=100)
                        _logger.info(f'Image successfully rendered in file "{filename}"')
                    else:
                        identifier = key
                    i += 1
            self.config.output = os.path.join(path, f'{identifier}.png')
        else:
            identifier = self.identifier

        if not identifier in self.config.pilots:
            _logger.error(f'{identifier} not found in pilots')
            _logger.error(f'Recognized pilots are : {", ".join(self.config.pilots.keys())}')
            raise Exception('Pilot not found !')
        pilot = self.config.pilots[identifier]

        img = self._get_pilot_img(pilot, base_img.width, base_img.height)
        paste(img, base_img)

    def _get_pilot_img(self, pilot:Pilot, width, height):
        pilot_name_length = len(pilot.name)
        has_long_pseudo =  pilot_name_length >= 15
        pilot_font = FontFactory.black(24 if has_long_pseudo else 30)
        return pilot.team._get_lineup_pilot_image(pilot, pilot_font, width, height, 138, has_long_pseudo)