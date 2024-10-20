import logging
import os.path
from dataclasses import dataclass

from src.media_generation.layout.image_layout import ImageLayout
from src.media_generation.layout.team.team_layout_mixin import TeamLayoutMixin

ASSETS_PATH = 'assets/teams'

_logger = logging.getLogger(__name__)


@dataclass
class TeamLogoLayout(ImageLayout, TeamLayoutMixin):
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
            _logger.debug(f"Will use {variant_filepath} for team logo")
            return variant_filepath
        default_path = os.path.join(ASSETS_PATH, team.filename)
        _logger.debug(f"Will use {default_path} for team logo")
        return default_path
