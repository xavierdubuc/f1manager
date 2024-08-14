from dataclasses import dataclass

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.models.pilot import Pilot
from src.media_generation.readers.race_reader_models.race import Race


@dataclass
class PilotLineupLayout(Layout):
    pilot: Pilot = None

    def _paste_children(self, img: PngImageFile, context: dict = {}):
        if self.pilot:
            updated_context = dict(context, pilot=self.pilot)
        else:
            updated_context = context
        super()._paste_children(img, updated_context)

    def _get_children_context(self, context: dict= {}):
        if self.pilot:
            return dict(context, pilot=self.pilot)
        return super()._get_children_context(context)
