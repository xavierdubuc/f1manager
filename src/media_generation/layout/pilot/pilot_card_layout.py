from dataclasses import dataclass
import logging

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.models.pilot import Pilot

_logger = logging.getLogger(__name__)


@dataclass
class PilotCardLayout(Layout):

    def _paste_child(self, img: PngImageFile, key: str, child: Layout, context: dict = ...):
        if key == 'pilot_name':
            child.bg = self._get_bg(context)
            child.fg = self._get_fg(context)
        super()._paste_child(img, key, child, context)

    def _get_children_context(self, context: dict = {}):
        if "pilot" in context:
            pilot: Pilot = context['pilot']
            if pilot:
                return dict(
                    context,
                    pilot_name=pilot.name.upper(),
                    team_logo_path=pilot.team.get_ranking_logo_path()
                )

        team_logo_path = ""
        pilot_name = ""
        if "official_pilot" in context:
            official_pilot = context["official_pilot"]
            pilot_name = (official_pilot or "").upper()

        return dict(
            context,
            pilot_name=pilot_name,
            team_logo_path=team_logo_path
        )
