from dataclasses import dataclass
from typing import Any, Dict


import os.path
from src.media_generation.layout.image_layout import ImageLayout
from src.media_generation.models.team import Team

ASSETS_PATH = 'assets/teams'


@dataclass
class TeamLogoLayout(ImageLayout):
    team: Team = None
    variant: str = 'results'

    def _get_path(self, context: dict = {}) -> str:
        team = self._get_team(context)
        if not team:
            return super()._get_path(context)
        return self._get_logo_path(context)

    def _get_logo_path(self, context: dict = {}) -> str:
        team = self._get_team(context)
        variant_filepath = os.path.join(ASSETS_PATH, self.variant, team.filename)
        if os.path.exists(variant_filepath):
            return variant_filepath
        return os.path.join(ASSETS_PATH, team.filename)

    def _get_team(self, context: Dict[str, Any] = {}) -> Team:
        return self._get_ctx_attr('team', context, use_format=False)
