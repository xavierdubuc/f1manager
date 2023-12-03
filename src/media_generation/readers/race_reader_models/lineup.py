from dataclasses import dataclass
from typing import Dict, List

from src.media_generation.models.pilot import Pilot


@dataclass
class LineUp:
    pilot_names: List[str]

    # "COMPUTED"
    pilots: Dict[str, Pilot] = None

    def __iter__(self):
        return iter(self.pilots or self.pilot_names)

    def __getitem__(self, key):
        return self.pilots and self.pilots.get(key, None)