import logging
import os
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.models.pilot import Pilot

from ..generators.abstract_generator import AbstractGenerator
from ..helpers.transform import *
from src.media_generation.data import teams_idx as TEAMS

_logger = logging.getLogger(__name__)

class PublicException(Exception):
    pass

class PilotGenerator(AbstractGenerator):
    def __init__(self, championship_config: dict, config: GeneratorConfig, season: int, identifier: str = None, *args, **kwargs):
        super().__init__(championship_config, config, season, identifier, *args, **kwargs)
        self.forced_team = kwargs.get('team')
        self.visual_type = kwargs.get('visual_type', 'lineup')

    def _get_visual_type(self) -> str:
        return 'pilot'

    def _generate_basic_image(self) -> PngImageFile:
        if self.visual_type == 'whole':
            size = (676, 1800)
        elif self.visual_type == 'face':
            size = (290, 290)
        elif self.visual_type == 'closeup':
            size = (200,200)
        else:
            size = (364, 210)
        return Image.new('RGBA', size, (0,0,0,0))

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
            pilots = "\n".join(f'- `{key}` ({self.config.pilots[key].team.name})' for key in self.config.pilots.keys())
            raise PublicException(f'Pilote non trouvé, les pilotes reconnus sont : \n{pilots}')
        pilot = self.config.pilots[identifier]

        img = self._get_pilot_img(pilot, base_img.width, base_img.height)
        paste(img, base_img)

    def _get_pilot_img(self, pilot:Pilot, width, height):
        if self.forced_team:
            pilot.team = TEAMS.get(self.forced_team, pilot.team)
        if self.visual_type == 'lineup':
            pilot_name_length = len(pilot.name)
            has_long_pseudo =  pilot_name_length >= 15
            pilot_font = FontFactory.black(24 if has_long_pseudo else 30)
            return pilot.team._get_lineup_pilot_image(pilot, pilot_font, width, height, 138, has_long_pseudo)
        if self.visual_type == 'face':
            return pilot.get_face_image()
        if self.visual_type == 'closeup':
            return pilot.get_close_up_image(138)
        if self.visual_type == 'whole':
            return pilot.get_long_range_image()
