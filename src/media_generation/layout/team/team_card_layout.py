from dataclasses import dataclass
from typing import Any, Dict, Tuple

from src.media_generation.layout.layout import DEFAULT_BG, Layout
from src.media_generation.layout.team.team_layout_mixin import TeamLayoutMixin
from src.media_generation.models.team import Team


@dataclass
class TeamCardLayout(TeamLayoutMixin):

    def _get_bg(self, context: Dict[str, Any] = {}) -> Tuple[int, int, int, int]:
        team = self._get_team(context)
        if self.bg != DEFAULT_BG or not team:
            return self._get_ctx_attr('bg', context)
        return team.standing_bg
