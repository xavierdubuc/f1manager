import logging
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngImageFile
from psd_tools import PSDImage

from ..font_factory import FontFactory
from ..helpers.transform import *
from .team import Team

_logger = logging.getLogger(__name__)

@dataclass
class Pilot:
    name: str
    team: Team = None
    number: str = 'Re'
    title: str = None
    reservist: bool = False
    trigram: str = None

    def __post_init__(self):
        if not self.trigram:
            for prefix in ('FBRT_', 'WSC_', 'VRA-', 'x0-', 'APX_', 'F1TEAM_', 'GT10_', 'RSC-'):
                if self.name.startswith(prefix):
                    self.trigram = self.name[len(prefix):len(prefix)+3].upper()
                    break
            else:
                self.trigram = self.name[:3].upper()

    # IMAGES FROM PSD

    @classmethod
    def get_close_up_psd(cls) -> PSDImage:
        return PSDImage.open('assets/pilots/all.psd')

    @classmethod
    def get_long_range_psd(cls) -> PSDImage:
        return PSDImage.open('assets/pilots/all.psd')

    def get_close_up_image(self, width=None, height=None) -> PngImageFile:
        # Silence all warnings from PSDImage
        initial_level = logging.getLogger().getEffectiveLevel()
        logging.getLogger().setLevel(logging.ERROR)
        psd = self.get_close_up_psd()
        logging.getLogger().setLevel(initial_level)
        return self._get_image_from_psd(psd, 0, 1, width, height, cropping_zone=(70, 0, 246, 176))

    def get_long_range_image(self) -> PngImageFile:
        # Silence all warnings from PSDImage
        initial_level = logging.getLogger().getEffectiveLevel()
        logging.getLogger().setLevel(logging.ERROR)
        psd = self.get_long_range_psd()
        logging.getLogger().setLevel(initial_level)
        return self._get_image_from_psd(psd, 0, 1)

    def has_image_in_close_up_psd(self) -> PngImageFile:
        psd = self.get_close_up_psd()
        return self._has_image_in_psd(psd, 0, 1)

    def has_image_in_long_range_psd(self) -> PngImageFile:
        psd = self.get_long_range_psd()
        return self._has_image_in_psd(psd, 0, 1)

    # GENERATED IMAGES

    def get_trigram_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        padding_box = 2
        padding_name_box = 4
        trigram_txt = text(self.trigram, (255, 255, 255), FontFactory.black(20))
        box = self.team.get_box_image(width=6, height=trigram_txt.height + padding_box * 2)
        box_pos = paste(box, img, left=padding_box, top=5)
        paste(trigram_txt, img, left=box_pos.right + padding_name_box)
        return img

    def get_image(self, width: int, height: int, pilot_font, pilot_color=(255,255,255), show_box:bool=False, box_width:int=0, box_height:int=0, name_top:int=False):
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
        paste(name_img, img, left = team_pos.right + 20, top=name_top)

        return img

    def get_ranking_image(self, width: int, height: int, pilot_font,
                          show_box: bool = False,
                          fg_color: tuple = (255,255,255,255),
                          bg_color: tuple=(0,0,0,0),
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

    @staticmethod
    def get_default_image() -> PngImageFile:
        return Image.open('assets/pilots/default.png')

    def get_name_image(self, font: ImageFont.FreeTypeFont, color: tuple = (255, 255, 255)) -> PngImageFile:
        return text(self.name.upper(), color, font)

    # PRIVATE

    def _get_number_image(self, font: ImageFont.FreeTypeFont) -> PngImageFile:
        return text(
            self.number,
            self.team.secondary_color,
            font,
            stroke_fill=self.team.main_color,
            stroke_width=3
        )

    def _get_image_from_psd(self, psd:PSDImage, faces_index=1, clothes_index=2, width:int=None, height:int=None, cropping_zone:tuple=False) -> PngImageFile:
        # FACE
        try:
            faces = psd[faces_index]
            faces.visible = True
        except IndexError:
            _logger.error(f'There is no "{faces_index}" in following psd, face calc index is probably wrong')
            _logger.error(psd)
            faces = []

        face_found = None
        for v in faces:
            v.visible = v.name == self.name
            if v.visible:
                face_found = v.name
        if face_found: 
            _logger.debug(f'Using "{face_found}" face')
        else:
            _logger.warning(f'No face found for pilot {self.name}, using default one')
            faces[0].visible = True # enable 'default' layer

        # CLOTHES
        try:
            clothes = psd[clothes_index]
            clothes.visible = True
        except IndexError:
            _logger.error(f'There is no "{clothes_index}" in following psd, face calc index is probably wrong')
            _logger.error(psd)
            clothes = []

        default_index = -1
        clothes_found = None
        for i, t in enumerate(clothes):
            if t.name == 'default':
                default_index = i
            t.visible = t.name.replace(' ','') == self.team.name if self.team else None
            if t.visible:
                clothes_found = t.name
        if clothes_found:
            _logger.debug(f'Using "{clothes_found}" clothes')
        else:
            _logger.warning(f'No clothes found for team {self.team.name}, using default one')
            clothes[default_index].visible = True

        base = psd.composite(layer_filter=lambda x:x.is_visible())

        # resizing
        if width and not height:
            height = width
        if height and not width:
            width = height
        if width and height:
            if cropping_zone:
                base = base.crop(cropping_zone)
            base = resize(base, width, height, keep_ratio=False)

        return base

    def _has_image_in_psd(self, psd:PSDImage, faces_index=1, clothes_index=2) -> PngImageFile:
        faces = psd[faces_index]
        for v in faces:
            if v.name == self.name:
                return True
        return False

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Pilot):
            return value.name == self.name
        if isinstance(value, str):
            return self.name == value
        return False
