from dataclasses import dataclass
import logging

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.layout.pilot.pilot_card_layout import PilotCardLayout
from src.media_generation.layout.text_layout import TextLayout
from src.media_generation.models.pilot import Pilot

_logger = logging.getLogger(__name__)

OFFICIAL_PILOT_BG = (200, 200, 200, 255)
OFFICIAL_PILOT_FG = (150, 150, 150, 255)
OFFICIAL_PILOT_STROKE = (100, 100, 100, 255)


@dataclass
class PilotNumberLayout(Layout):
    def _get_colors(self, context: dict):
        if "pilot" in context:
            pilot: Pilot = context['pilot']
            if pilot:
                return pilot.team.standing_fg, pilot.team.standing_bg, pilot.team.main_color, pilot.team.secondary_color
        if "official_pilot" in context and context["official_pilot"]:
            return OFFICIAL_PILOT_FG, OFFICIAL_PILOT_BG, OFFICIAL_PILOT_FG, OFFICIAL_PILOT_STROKE
        return (255,255,255), (0, 0, 0, 0), (255,255,255), (0, 0, 0, 255)

    def _paste_child(self, img: PngImageFile, key: str, child: Layout, context: dict = ...):
        fg, bg, stroke_around, stroke = self._get_colors(context)
        if isinstance(child, TextLayout):
            child.fg = stroke_around
            child.stroke_fill = stroke
        elif isinstance(child, PilotCardLayout):
            child.fg = fg
            child.bg = bg
        super()._paste_child(img, key, child, context)
