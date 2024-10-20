from dataclasses import dataclass, field
import logging
from typing import Any, Dict, List

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.models.pilot import Pilot

_logger = logging.getLogger(__name__)

DEFAULT_LOCKED_NUMBERS = {
    1: "-",
    2: "Sargeant",
    3: "Ricciardo",
    4: "Norris",
    10: "Gasly",
    11: "Perez",
    14: "Alonso",
    16: "Leclerc",
    17: "/",
    18: "Stroll",
    20: "Magnussen",
    22: "Tsunoda",
    23: "Albon",
    24: "Zhou",
    27: "Hulkenberg",
    31: "Ocon",
    33: "Verstappen",
    44: "Hamilton",
    55: "Sainz",
    63: "Russell",
    77: "Bottas",
    81: "Piastri"
}


@dataclass
class PilotNumbersLayout(Layout):
    locked_numbers: Dict[str, str] = field(default_factory=lambda: DEFAULT_LOCKED_NUMBERS)

    def _get_template_instance_context(self, i: int, context: Dict[str, Any] = {}):
        config = context.get('config', None)
        if not config:
            return None
        ctx = {'number': i+1}
        if self.locked_numbers:
            ctx['official_pilot'] = self.locked_numbers.get(i+1)

        ctx['pilot'] = None
        if config.pilots:
            for p in config.pilots.values():
                if p.number.isnumeric() and int(p.number) == i+1:
                    ctx['pilot'] = p

        return ctx
