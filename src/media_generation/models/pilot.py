from dataclasses import dataclass

from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngImageFile
from psd_tools import PSDImage

from ..font_factory import FontFactory
from ..helpers.transform import paste, text
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

    def get_image(self, width: int, height: int, number_font, pilot_font):
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        draw_canvas = ImageDraw.Draw(img)
        # NUMBER
        pos_left = 2 if len(self.number) == 2 else 12
        draw_canvas.text(
            (pos_left, 14),
            self.number,
            fill=self.team.secondary_color,
            stroke_fill=self.team.main_color,
            stroke_width=3,
            font=number_font
        )

        # NAME
        left_name = 70
        draw_canvas.text(
            (left_name, 14),
            self.name,
            (255, 255, 255),
            pilot_font
        )

        # TEAM
        with Image.open(self.get_team_image()) as team_image:
            padding = 4
            image_size = height - padding
            team_image.thumbnail((image_size, image_size), Image.Resampling.LANCZOS)
            img.paste(team_image, ((width - team_image.width) - padding, padding//2), team_image)

        return img

    def get_ranking_image(self, position: int, width: int, height: int, number_font, pilot_font, has_fastest_lap: bool = False, with_fastest_img: bool = True):
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))

        if has_fastest_lap:
            bg_color = (180, 60, 220)
        else:
            bg_color = (0, 0, 0)
        grid_position_bg = Image.new('RGB', (width, height), bg_color)
        alpha = Image.linear_gradient('L').rotate(-90).resize((width, height))
        grid_position_bg.putalpha(alpha)
        img.paste(grid_position_bg, (5, 0))

        white_box_width = height
        with Image.open(f'assets/position.png') as tmp:
            grid_position_number = tmp.copy().convert('RGBA')
            grid_position_number.thumbnail((white_box_width, height), Image.Resampling.LANCZOS)
            txt = text(str(position), (0,0,0), FontFactory.regular(20))
            paste(txt, grid_position_number)
            paste(grid_position_number, img, left=0)

        pilot_image = self.get_image(width - (white_box_width+15), height, number_font, pilot_font)
        img.paste(pilot_image, (white_box_width+15, 0), pilot_image)
        if has_fastest_lap and with_fastest_img:
            with Image.open(f'assets/fastest_lap.png') as fstst_img:
                fstst_img.thumbnail((height, height), Image.Resampling.LANCZOS)
                img.paste(fstst_img, (width-fstst_img.width * 2, 0))

        return img
