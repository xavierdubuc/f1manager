from dataclasses import dataclass

from PIL import Image, ImageFont
from PIL.PngImagePlugin import PngImageFile

from src.media_generation.font_factory import FontFactory
from src.media_generation.helpers.transform import paste, resize, text
from src.media_generation.models.team import Team


@dataclass
class Pilot:
    name: str
    team: Team = None
    number: str = 'Re'
    title: str = None
    reservist: bool = False
    aspirant: bool = False
    trigram: str = None
    psd_name: str = None

    def __post_init__(self):
        if not self.trigram:
            for prefix in ('FBRT_', 'WSC_', 'VRA-', 'x0-', 'APX_', 'F1TEAM_', 'GT10_', 'RSC-', 'VR1_'):
                if self.name.startswith(prefix):
                    self.trigram = self.name[len(prefix):len(prefix)+3].upper()
                    break
            else:
                self.trigram = self.name[:3].upper()
        if not self.psd_name:
            self.psd_name = self.name

    # GENERATED IMAGES

    def get_trigram_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        padding_box = 2
        padding_name_box = 4
        trigram_txt = text(self.trigram, (255, 255, 255), FontFactory.black(20))
        box = self.team.get_box_image(width=6, height=trigram_txt.height + padding_box * 2)
        box_pos = paste(box, img, left=padding_box, top=5)
        paste(trigram_txt, img, left=box_pos.right + padding_name_box)
        return img

    def get_image(self, width: int, height: int, pilot_font, pilot_color=(255, 255, 255), show_box: bool = False, box_width: int = 0, box_height: int = 0, name_top: int = False):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # BOX (if applicable)
        if show_box:
            box_img = self.team.get_box_image(box_width, box_height)
            paste(box_img, img, left=0)

        # TEAM
        image_size = .75 * height
        team_logo = self._get_team_logo_image(image_size, image_size)
        team_pos = paste(team_logo, img, left=box_width + 20)

        # NAME
        name_img = self.get_name_image(pilot_font, pilot_color)
        paste(name_img, img, left=team_pos.right + 20, top=name_top)

        return img

    def get_ranking_image(self, width: int, height: int, pilot_font,
                          show_box: bool = False,
                          fg_color: tuple = (255, 255, 255, 255),
                          bg_color: tuple = (0, 0, 0, 0),
                          name_top: int = False) -> PngImageFile:
        img = Image.new('RGBA', (width, height), bg_color)

        # [BOX] [LOGO] [PILOT NAME]
        box_width = 5
        box_height = int(0.75 * height)

        pilot_image = self.get_image(width, height, pilot_font, fg_color, show_box, box_width, box_height, name_top)
        paste(pilot_image, img, left=0, top=0)
        return img

    def _get_team_logo_image(self, width: int, height: int) -> PngImageFile:
        with self.team.get_results_logo() as team_logo:
            team_logo = resize(team_logo, width, height)
        return team_logo

    def get_name_image(self, font: ImageFont.FreeTypeFont, color: tuple = (255, 255, 255)) -> PngImageFile:
        return text(self.name.upper(), color, font)

    # PRIVATE

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Pilot):
            return value.name == self.name
        if isinstance(value, str):
            return self.name == value
        return False
