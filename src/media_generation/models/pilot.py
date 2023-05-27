from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngImageFile
from psd_tools import PSDImage

from ..font_factory import FontFactory
from ..helpers.transform import *
from .team import Team


@dataclass
class Pilot:
    name: str
    team: Team = None
    number: str = 'Re'
    title: str = None
    reservist: bool = False

    @classmethod
    def get_close_up_psd(cls) -> PSDImage:
        return PSDImage.open('assets/pilots/closeup.psd')

    @classmethod
    def get_long_range_psd(cls) -> PSDImage:
        return PSDImage.open('assets/pilots/longrange.psd')

    def get_close_up_image(self) -> PngImageFile:
        psd = self.get_close_up_psd()
        return self._get_image_from_psd(psd, 2, 3)

    def get_long_range_image(self) -> PngImageFile:
        psd = self.get_long_range_psd()
        return self._get_image_from_psd(psd, 1, 2)

    def has_image_in_close_up_psd(self) -> PngImageFile:
        psd = self.get_close_up_psd()
        return self._has_image_in_psd(psd, 2, 3)

    def has_image_in_long_range_psd(self) -> PngImageFile:
        psd = self.get_long_range_psd()
        return self._has_image_in_psd(psd, 2, 3)

    @classmethod
    def rename_psd_layers(cls, psd, faces_index=1, clothes_index=2):
        faces = psd[faces_index]
        clothes = psd[clothes_index]
        rename_map = {
            "x_Kayyzor":"xKayysor",
            "?":"x0-STEWEN_26-0x",
            "!":"VRA-RedAym62",
            "majforti":"majforti-07",
            "gregy":"WSC_Gregy21",
            "FBRT_Seb":"FBRT_Seb07",
            "Iceman":"Iceman7301",
            "FBRT_CID":"FBRT_CiD16",
        }
        for v in faces:
            v.name = v.name.replace(' détouré', '')
            v.name = rename_map.get(v.name, v.name)

        for t in clothes:
            t.name = t.name.replace(' ', '')

        psd.save('assets/pilots/renamed.psd')

    def get_image(self, width: int, height: int, pilot_font, pilot_color=(255,255,255), show_box:bool=False, box_width:int=0, box_height:int=0):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # BOX (if applicable)
        if show_box:
            box_img = self.team.get_box_image(box_width, box_height)
            paste(box_img, img, left=0, use_obj=True)

        # TEAM
        padding = 8
        image_size = height - padding
        team_logo = self._get_team_logo_image(image_size, image_size)
        team_pos = paste(team_logo, img, left=box_width + 20, use_obj=True)

        # NAME
        name_img = self.get_name_image(pilot_font, pilot_color)
        paste(name_img, img, left = team_pos.right + 20, top=14, use_obj=True)

        return img

    def get_ranking_image(self, width: int, height: int, pilot_font,
                          show_box: bool = False,
                          fg_color: tuple = (255,255,255,255),
                          bg_color: tuple=(0,0,0,0)) -> PngImageFile:
        img = Image.new('RGBA', (width, height), bg_color)

        # [BOX] [LOGO] [PILOT NAME]
        box_width = 5
        box_height = int(0.75 * height)

        pilot_image = self.get_image(width, height, pilot_font, fg_color, show_box, box_width, box_height)
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

    def _get_number_image(self, font: ImageFont.FreeTypeFont) -> PngImageFile:
        return text(
            self.number,
            self.team.secondary_color,
            font,
            stroke_fill=self.team.main_color,
            stroke_width=3
        )

    def _get_image_from_psd(self, psd:PSDImage, faces_index=1, clothes_index=2) -> PngImageFile:
        faces = psd[faces_index]
        clothes = psd[clothes_index]
        for v in faces:
            v.visible = v.name == self.name
        for t in clothes:
            t.visible = t.name == self.team.name if self.team else None
        return psd.composite(layer_filter=lambda x:x.is_visible())

    def _has_image_in_psd(self, psd:PSDImage, faces_index=1, clothes_index=2) -> PngImageFile:
        faces = psd[faces_index]
        for v in faces:
            if v.name == self.name:
                return True
        return False
