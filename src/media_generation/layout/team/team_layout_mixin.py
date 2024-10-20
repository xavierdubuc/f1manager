from dataclasses import dataclass
from typing import Any, Dict

from src.media_generation.layout.layout import Layout
from src.media_generation.models.team import Team


@dataclass
class TeamLayoutMixin(Layout):
    team: Team = None

    def _get_team(self, context: Dict[str, Any] = {}) -> Team:
        return self._get_ctx_attr('team', context, use_format=False)
