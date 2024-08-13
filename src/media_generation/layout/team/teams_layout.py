import logging

from dataclasses import dataclass
from typing import Dict, List

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.models.team import Team
from src.media_generation.readers.race_reader_models.race import Race

_logger = logging.getLogger(__name__)


@dataclass
class TeamsLayout(Layout):
    positions: List[Dict[str, int]] = None

    def _paste_children(self, img: PngImageFile, context: dict = {}):
        config = context.get('config', None)
        if config and config.teams:
            teams:List[Team] = config.teams
        else:
            teams:List[Team] = context.get('teams', {}).values()
            
        for team, position in zip(teams, self.positions):
            for key, child in self.children.items():
                child.team = team
                child.left = position['left']
                child.top = position['top']
                _logger.debug(f'Pasting {key} on layout {self.__class__.__name__} for team {team.name}')
                child.paste_on(img, context)
