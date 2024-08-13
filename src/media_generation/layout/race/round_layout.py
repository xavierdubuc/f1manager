from dataclasses import dataclass

from PIL.PngImagePlugin import PngImageFile
from PIL import Image, ImageDraw


from src.media_generation.layout.layout import Layout
from src.media_generation.layout.text_layout import TextLayout
from src.media_generation.readers.race_reader_models.race import Race, RaceType

SANDBOX_IMG = Image.new('RGB', (5000, 5000))
SANDBOX = ImageDraw.Draw(SANDBOX_IMG)
DEFAULT_FONT_SIZE = 200
METHOD_FONTS = [
    "polebg", "regular", "bold", "black", "wide"
]


@dataclass
class RoundLayout(Layout):
    sprint_bg = (0, 200, 200, 240)
    double_grid_bg = (200, 200, 0, 240)
    full_length_bg = (200, 100, 200, 240)
    default_bg = (220, 0, 0, 240)

    sprint_fg = (255, 255, 255, 255)
    double_grid_fg = (255, 255, 255, 255)
    full_length_fg = (255, 255, 255, 255)
    default_fg = (255, 255, 255, 255)

    def _render_base_image(self, context: dict = {}) -> PngImageFile:
        self.bg = self.default_bg
        self.fg = self.default_fg
        race:Race = context.get('race', None)
        if race_type := (race.type if race else None):
            if race_type in (RaceType.SPRINT_1, RaceType.SPRINT_2, RaceType.FULL_LENGTH):
                if 'subtype_top' not in self.children:
                    self.children['subtype_top'] = TextLayout(
                        name='subtype_top',
                        width=self.width,
                        height=self.height,
                        top=10
                    )
                if race_type == RaceType.FULL_LENGTH:
                    self.bg = self.full_length_bg
                    self.fg = self.full_length_fg
                    self.children['subtype_top'].content = '100%'
                else:
                    self.children['subtype_top'].content = 'SPRINT'
                    self.bg = self.sprint_bg
                    self.fg = self.sprint_fg
            elif race_type in (RaceType.DOUBLE_GRID_1, RaceType.DOUBLE_GRID_2):
                if 'subtype_top' not in self.children:
                    self.children['subtype_top'] = TextLayout(
                        name="subtype_top",
                        width=self.width,
                        height=self.height,
                        top=10
                    )
                self.children['subtype_top'].content = 'DOUBLE'
                if 'subtype_bottom' not in self.children:
                    self.children['subtype_bottom'] = TextLayout(
                        name="subtype_bottom",
                        width=self.width,
                        height=self.height,
                        bottom=10
                    )
                self.children['subtype_bottom'].content = 'GRID'
                self.bg = self.double_grid_bg
                self.fg = self.double_grid_fg
            for child in self.children.values():
                child.bg = self.bg
                child.fg = self.fg

        return super()._render_base_image(context)
