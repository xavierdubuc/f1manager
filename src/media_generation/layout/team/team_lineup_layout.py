from dataclasses import dataclass
from typing import Any, Dict, List

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.layout.layout import Layout
from src.media_generation.models.pilot import Pilot
from src.media_generation.models.team import Team
from src.media_generation.readers.race_reader_models.race import Race


@dataclass
class TeamLineupLayout(Layout):
    pilots: List[Pilot] = None

    def _get_pilots(self, context: Dict[str, Any] = {}) -> List[Pilot]:
        if not self.pilots:
            team = context.get('team')
            if not team:
                self.pilots = []
            race: Race = context.get('race')
            if race:
                self.pilots = race.get_pilots(team)
            else:
                config: GeneratorConfig = context.get('config')
                self.pilots = config.get_pilots(team) if config else []
        return self.pilots

    def _paste_child(self, img: PngImageFile, key: str, child: Layout, context: Dict[str, Any] = {}):
        team: Team = context.get('team')
        if not team:
            return  # if no team, then don't paste anything

        if key == 'logo':
            child.path = team.get_lineup_logo_path()
        elif key == 'pilot_1':
            pilots = self._get_pilots(context)
            context['pilot'] = pilots[0] if pilots and len(pilots) > 0 else None
        elif key == 'pilot_2':
            pilots = self._get_pilots(context)
            context['pilot'] = pilots[1] if pilots and len(pilots) > 1 else None
        return super()._paste_child(img, key, child, context)
