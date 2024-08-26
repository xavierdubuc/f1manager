from dataclasses import dataclass

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.helpers.transform import resize
from src.media_generation.layout.layout import Layout
from src.media_generation.models.pilot import Pilot
from src.media_generation.readers.race_reader_models.race import Race

FACE = 'RACE'
WHOLE = 'WHOLE'

@dataclass
class PilotPhotoLayout(Layout):
    photo_type:str=FACE

    def _render_base_image(self, context: dict = {}) -> PngImageFile:
        pilot:Pilot = context.get('pilot')
        if not pilot:
            # TODO get default image ?
            return super()._render_base_image(context)
        if self.photo_type == FACE:
            return pilot.get_close_up_image(height=self.height, width=self.width)
        img = pilot.get_long_range_image()
        return resize(img, self.width, self.height)

