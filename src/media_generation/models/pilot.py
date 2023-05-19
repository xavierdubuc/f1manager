from dataclasses import dataclass

from PIL import Image, ImageDraw
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

    def get_long_range_image(self):
        psd = self.get_long_range_psd()
        return self._get_image_from_psd(psd, 1, 2)

    def _get_image_from_psd(self, psd:PSDImage, faces_index=1, clothes_index=2):
        faces = psd[faces_index]
        clothes = psd[clothes_index]
        for v in faces:
            v.visible = v.name == self.name
        for t in clothes:
            t.visible = t.name == self.team.name if self.team else None
        return psd.composite(layer_filter=lambda x:x.is_visible())

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

    def get_team_image(self):
        return self.team.get_image() if self.team else ''

    def get_image(self, width: int, height: int, pilot_font):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        # TEAM
        with self.team.get_results_image() as team_image:
            padding = 8
            image_size = height - padding
            team_image = resize(team_image, image_size, image_size)
            team_pos = paste(team_image, img, left=0, use_obj=True)

        # NUMBER
        # pos_left = 10 if len(self.number) == 2 else 20
        # number_img = text(
        #     self.number,
        #     self.team.secondary_color,
        #     number_font,
        #     stroke_fill=self.team.main_color,
        #     stroke_width=3
        # )
        # number_pos = paste(number_img, img, left=team_pos.right + pos_left, use_obj=True)

        # NAME
        name_img = text(
            self.name.upper(),
            (255,255,255),
            font=pilot_font
        )
        paste(name_img, img, left = team_pos.right + 20, top=14, use_obj=True)

        return img

    def get_ranking_image(self, position: int, width: int, height: int, pilot_font, has_fastest_lap: bool = False):

        if has_fastest_lap:
            bg_color = (160, 25, 190, 255)
        else:
            bg_color = (30, 30, 30, 235)
        img = Image.new('RGBA', (width, height), bg_color)

        left_padding = 10
        pos_img = self._get_position_image(position, height, height)
        left = left_padding + (height-pos_img.width) // 2
        paste(pos_img, img, left=left, use_obj=True)
        position_right = left_padding + height

        # box
        space = 10
        box_width = 5
        box_height = int(0.75 * height)
        draw = ImageDraw.Draw(img)
        box_top_left = (position_right + space, (height-box_height)//2)
        box_bot_right = (box_top_left[0] + box_width, box_top_left[1] + box_height)
        if not has_fastest_lap:
            draw.rectangle((box_top_left, box_bot_right), fill=self.team.box_color)

        space_with_pos = space + box_width + 2*space
        pilot_image = self.get_image(width - (position_right + space_with_pos), height, pilot_font)
        img.paste(pilot_image, (position_right+space_with_pos, 0), pilot_image)

        return img

    def _get_position_image(self, position: int, width:int, height:int,
                            font:ImageFont.FreeTypeFont=FontFactory.regular(30),
                            color=(255,255,255)):
        return text(str(position), color, font)

