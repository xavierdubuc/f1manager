from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngImageFile
from src.media_generation.font_factory import FontFactory
from src.media_generation.helpers.transform import line, paste, resize, text
from src.media_generation.data import teams_idx
from src.media_generation.models.pilot import Pilot
from src.telemetry.models.damage import Damage
from src.telemetry.models.enums.team import Team
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
        pilot_img = self._get_pilot_image(270, 65, participant)
        paste(pilot_img, out, top = 0)
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

    def _get_pilot_image(self, width:int, height:int, participant):
        img = Image.new('RGBA', (width*5, height*5))
        font_size = 120
        if len(participant.name) >= 16:
            font_size = 80 if '_' in participant.name or '-' in participant.name else 70
        elif len(participant.name) >= 14:
            font_size = 100 if '_' in participant.name or '-' in participant.name else 90
        elif len(participant.name) >= 12:
            font_size = 100 if '_' in participant.name or '-' in participant.name else 90
        font = FontFactory.black(font_size)

        if participant.team == Team.mclaren:
            team_str = 'McLaren'
        elif participant.team == Team.red_bull_racing:
            team_str = 'RedBull'
        else:
            team_str = participant.team.name.title().replace('_','')
        team = teams_idx[team_str]
        pilot = Pilot(participant.name, team, participant.race_number)

        logo_width = .75 * img.height
        logo_img = pilot._get_team_logo_image(logo_width, logo_width)
        name_img = pilot.get_name_image(font, (255,255,255))
        space_between = 40
        logo_and_name_total_width = logo_img.width + space_between + name_img.width

        logo_pos = paste(logo_img, img, left=(img.width-logo_and_name_total_width) // 2)
        paste(name_img, img, left = logo_pos.right + space_between)

        return resize(img, width, height)
