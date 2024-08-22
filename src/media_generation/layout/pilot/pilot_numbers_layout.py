from dataclasses import dataclass, field
import logging
from typing import Any, Dict, List

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.models.pilot import Pilot

_logger = logging.getLogger(__name__)


@dataclass
class PilotNumbersLayout(Layout):
    locked_numbers: Dict[str, str] = field(default_factory=dict)

    def _get_template_instance_context(self, i: int, context: Dict[str, Any] = {}):
        config = context.get('config', None)
        if not config:
            return {}
        ctx = {'number': i+1}
        if self.locked_numbers:
            ctx['official_pilot'] = self.locked_numbers.get(i+1)

        ctx['pilot'] = None
        if config.pilots:
            for p in config.pilots.values():
                if p.number.isnumeric() and int(p.number) == i+1:
                    ctx['pilot'] = p

        return ctx
