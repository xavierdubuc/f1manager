from dataclasses import dataclass

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.models.pilot import Pilot
from src.media_generation.models.team import Team
from src.media_generation.readers.race_reader_models.race import Race


@dataclass
class PilotBoxLayout(Layout):

    def _render_base_image(self, context: dict = {}) -> PngImageFile:
        team: Team = context.get('team')
        pilot: Pilot = context.get('pilot')
        if pilot:
            team = pilot.team
        if not team:
            return super()._render_base_image(context)
        
        for child in self.children.values():
            child.fg = team.lineup_fg_color
            child.bg = team.lineup_bg_color
        return team.get_parallelogram(self.width, self.height)

    def _get_children_context(self, context: dict= {}):
        pilot: Pilot = context.get('pilot')
        if not pilot:
            return dict(context, pilot_name="?")
        return dict(context, pilot_name=pilot.name.upper())
