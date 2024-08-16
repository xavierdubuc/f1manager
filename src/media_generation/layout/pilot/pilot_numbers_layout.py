from dataclasses import dataclass
import logging
from typing import Dict, List

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.models.pilot import Pilot

_logger = logging.getLogger(__name__)


@dataclass
class PilotNumbersLayout(Layout):
    locked_numbers: Dict[str, str] = None
    positions: List[Dict[str, int]] = None

    def _paste_children(self, img: PngImageFile, context: dict = {}):
        config = context.get('config', None)
        if not config:
            return
        if not config.pilots:
            return
        pilots: Dict[int, Pilot] = {
            int(p.number): p for p in config.pilots.values() if p.number and p.number != 'Re'
        }
        official_pilots: Dict[int, str] = self.locked_numbers
        for i, position in enumerate(self.positions):
            number = i+1
            context['number'] = number
            context['pilot'] = pilots.get(number)
            context['official_pilot'] = official_pilots.get(number)
            for key, child in self.children.items():
                child.left = position['left']
                child.top = position['top']
                _logger.debug(f'Pasting {key} on layout {self.__class__.__name__} for number {i}')
                child.paste_on(img, context)
