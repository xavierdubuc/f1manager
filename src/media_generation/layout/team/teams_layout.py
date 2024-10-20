import logging

from dataclasses import dataclass
from typing import Any, Dict, List

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.models.team import Team
from src.media_generation.readers.race_reader_models.race import Race

_logger = logging.getLogger(__name__)


@dataclass
class TeamsLayout(Layout):
    teams: List[Team] = None

    def _get_teams(self, context: Dict[str, Any] = {}) -> List[Team]:
        if self.teams is None:
            config = context.get('config')
            if config and config.teams:
                teams: List[Team] = config.teams
            else:
                teams: List[Team] = context.get('teams', [])
            self.teams = list(teams.values()) if isinstance(teams, dict) else teams
        return self.teams

    def _get_template_instance_context(self, i: int, context: Dict[str, Any] = {}):
        teams = self._get_teams(context)
        if not teams:
            return super()._get_template_instance_context(i, context)
        if 0 <= i < len(teams):
            return {"team": teams[i]}
        return None
