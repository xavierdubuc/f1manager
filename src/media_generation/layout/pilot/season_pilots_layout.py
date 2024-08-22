from dataclasses import dataclass
import logging
from typing import Any, Dict, List

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.models.pilot import Pilot

_logger = logging.getLogger(__name__)


@dataclass
class SeasonPilotsLayout(Layout):
    pilots: List[Pilot] = None

    def _get_pilots(self, context: Dict[str, Any] = {}) -> List[Pilot]:
        if self.pilots is None:
            config = context.get('config')
            if not config:
                return []
            if not config.pilots:
                return []
            pilots: List[Pilot] = list(config.pilots.values())
            identifier = context.get('identifier', 'all')
            if identifier == 'main':
                pilots = pilots[:20]
            elif identifier in ('reservist', 'reservists'):
                pilots = pilots[20:]
            self.pilots = pilots
        return self.pilots

    def _get_template_instance_context(self, i: int, context: Dict[str, Any] = {}):
        pilots = self._get_pilots(context)
        if not pilots:
            return super()._get_template_instance_context(i, context)
        if 0 <= i < len(pilots):
            pilot = pilots[i]
            return {
                'number': pilot.number,
                'pilot': pilot
            }
        return {
            'number': None,
            'pilot': None
        }
