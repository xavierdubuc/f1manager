from dataclasses import dataclass
import logging
from typing import Dict, List

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.models.pilot import Pilot

_logger = logging.getLogger(__name__)


@dataclass
class SeasonPilotsLayout(Layout):
    positions: List[Dict[str, int]] = None

    def _paste_children(self, img: PngImageFile, context: dict = {}):
        config = context.get('config', None)
        if not config:
            return
        if not config.pilots:
            return
        pilots: List[Pilot] = list(config.pilots.values())
        identifier = context.get('identifier', 'all')
        if identifier == 'main':
            pilots = pilots[:20]
        elif identifier in ('reservist', 'reservists'):
            pilots = pilots[20:]

        for pilot, position in zip(pilots, self.positions):
            context['number'] = pilot.number
            context['pilot'] = pilot
            for key, child in self.children.items():
                child.left = position['left']
                child.top = position['top']
                _logger.debug(f'Pasting {key} on layout {self.__class__.__name__} for {pilot.number} {pilot.name}')
                child.paste_on(img, context)
