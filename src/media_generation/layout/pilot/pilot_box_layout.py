from dataclasses import dataclass

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.models.pilot import Pilot
from src.media_generation.readers.race_reader_models.race import Race


@dataclass
class PilotBoxLayout(Layout):

    def _render_base_image(self, context: dict = {}) -> PngImageFile:
        pilot: Pilot = context.get('pilot')
        if not pilot:
            return super()._render_base_image(context)
        for child in self.children.values():
            child.fg = pilot.team.lineup_fg_color
            child.bg = pilot.team.lineup_bg_color
        return pilot.team.get_parallelogram(self.width, self.height)

    def _paste_children(self, img: PngImageFile, context: dict = {}):
        pilot: Pilot = context.get('pilot')
        if not pilot:
            ctx = context
        else:
            ctx = dict(context, pilot_name=pilot.name.upper())
        super()._paste_children(img, ctx)
