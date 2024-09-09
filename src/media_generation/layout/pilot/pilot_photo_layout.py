from dataclasses import dataclass

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.helpers.pilot_image_manager import PilotImageManager
from src.media_generation.helpers.transform import resize
from src.media_generation.layout.layout import Layout
from src.media_generation.models.pilot import Pilot

FACE = 'RACE'
WHOLE = 'WHOLE'


@dataclass
class PilotPhotoLayout(Layout):
    photo_type: str = FACE

    def _render_base_image(self, context: dict = {}) -> PngImageFile:
        pilot: Pilot = context.get('pilot')
        if not pilot:
            # TODO get default image ?
            return super()._render_base_image(context)
        manager = PilotImageManager()
        if self.photo_type == FACE:
            return manager.get_close_up_image(pilot, height=self.height, width=self.width)
        img = manager.get_long_range_image(pilot)
        return resize(img, self.width, self.height)
