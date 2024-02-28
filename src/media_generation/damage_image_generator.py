from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngImageFile
from src.media_generation.font_factory import FontFactory
from src.media_generation.helpers.transform import line, paste, text
from src.telemetry.models.damage import Damage
from src.telemetry.models.participant import Participant

ASSETS_DIR = 'assets/damages'
COLOR_STATUSES = ['lightgreen', 'green', 'yellow', 'orange', 'red']
PARTS = [
    'front_left_tyre',
    'front_right_tyre',
    'rear_left_tyre',
    'rear_right_tyre',
    'diffuser',
    'front_left_wing',
    'front_right_wing',
    'floor',
    'rear_wing',
    'sidepod'
]

PARTS_POSITIONS = {
    'front_left_tyre': (2,210),
    'front_right_tyre': (218,210),
    'rear_left_tyre': (1,495),
    'rear_right_tyre': (218,495),
    'diffuser': (112,455),
    'front_left_wing': (65,145),
    'front_right_wing': (155,145),
    'floor': (108,330),
    'rear_wing': (108,525),
    'sidepod': (2,360)
}

BLACK_BG_POSITIONS = {
    'diffuser': ((110,454), (162, 470)),
}

LINES_POSITIONS = {
    'floor': [
        ((120,348), (108, 362)),
        ((142,348), (154, 362)),
    ],
    'sidepod': [
        ((54,366), (80, 316)),
        ((54,366), (80, 416)),
    ]
}

class DamageImageGenerator:
    def __init__(self):
        self.base_image = Image.open(f'{ASSETS_DIR}/base.png').convert('RGBA')
        self.images = {}
        for part in PARTS:
            self.images[part] = {}
            for color in COLOR_STATUSES:
                self.images[part][color] = Image.open(f'{ASSETS_DIR}/{part}/{color}.png').convert('RGBA')

    def generate(self, damage:Damage, participant:Participant):
        out = self.base_image.copy()
        font_size = 26
        if len(participant.name) >= 16:
            font_size = 22 if '_' in participant.name or '-' in participant.name else 20
        elif len(participant.name) >= 13:
            font_size = 24 if '_' in participant.name or '-' in participant.name else 22
        name = text(participant.name.upper(), (255,255,255), FontFactory.black(font_size))

        paste(name, out, top = 20)
        self._paste_parts_images(out, damage)
        self._paste_parts_percents(out, damage)
        path = f'output/damages/{participant.name.lower()}.png'
        out.save(path, quality=95)
        return path

    def _paste_parts_images(self, img:PngImageFile, damage:Damage):
        for part in PARTS:
            if 'tyre' in part:
                value = getattr(damage, f'get_{part}_damage_value')()
            else:
                value = getattr(damage, f'{part}_damage')
            color = damage.get_component_color(value)
            paste(self.images[part][color], img)

    def _paste_parts_percents(self, img:PngImageFile, damage:Damage):
        font = FontFactory.regular(16)
        color = (255,255,255)
        for part in PARTS:
            if 'tyre' in part:
                value = getattr(damage, f'get_{part}_damage_value')()
            else:
                value = getattr(damage, f'{part}_damage')
            if value == 0:
                continue

            # lines
            if part in LINES_POSITIONS:
                lines = LINES_POSITIONS[part]
                for l in lines:
                    line(l, img, (255,255,255), 2)

            # BG
            if part in BLACK_BG_POSITIONS:
                xy = BLACK_BG_POSITIONS[part]
                draw = ImageDraw.Draw(img)
                draw.rounded_rectangle(xy, radius=0, fill=(30,30,30))

            # %
            value_str = f'{str(value).rjust(3)}%'
            position = PARTS_POSITIONS[part]
            paste(text(value_str, color, font), img, left=position[0], top=position[1])
