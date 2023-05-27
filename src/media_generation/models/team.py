from dataclasses import dataclass
from typing import List, Union
from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngImageFile
from ..font_factory import FontFactory
from ..helpers.transform import *


@dataclass
class Team:
    name: str
    title: str
    subtitle: str
    main_color: Union[str,tuple] = 'white'
    secondary_color: Union[str,tuple] = 'black'
    box_color: Union[str,tuple] = 'black'
    lineup_bg_color: Union[str,tuple] = 'black'
    standing_bg: Union[str,tuple] = 'black'
    standing_fg: Union[str,tuple] = 'white'
    breaking_fg_color: Union[str,tuple] = (255, 255, 255)
    breaking_bg_color: Union[str,tuple] = (255, 255, 255)
    breaking_line_color: Union[str,tuple] = (0, 0, 0)
    breaking_use_white_logo: bool = False
    pole_fg_color: Union[str,tuple] = None
    pole_bg_color: Union[str,tuple] = None
    pole_line_color: Union[str,tuple] = None

    def get_pole_colors(self):
        return {
            'fg': self.pole_fg_color if self.pole_fg_color else self.breaking_fg_color,
            'bg': self.pole_bg_color if self.pole_bg_color else self.breaking_bg_color,
            'line': self.pole_line_color if self.pole_line_color else self.breaking_line_color
        }

    def get_results_logo(self):
        if self.name == 'AlphaTauri':
            return Image.open(self.get_white_logo())
        return Image.open(self.get_image())

    def get_lineup_logo(self):
        if self.name in ('Alpine', 'AlfaRomeo', 'AlphaTauri', 'RedBull', 'AstonMartin', 'McLaren', 'Williams', 'Ferrari'):
            return Image.open(self.get_alt_logo())
        return Image.open(self.get_image())

    def get_image(self):
        return f'assets/teams/{self.name}.png'

    def get_breaking_logo(self):
        return self.get_white_logo() if self.breaking_use_white_logo else self.get_image()

    def get_white_logo(self):
        return f'assets/teams/white/{self.name}.png'

    def get_alt_logo(self):
        return f'assets/teams/alt/{self.name}.png'

    def get_team_image(self, width, title_font):
        line_separation = 10
        box_width = 10
        v_padding = 10
        title_width, title_height = text_size(self.title.upper(), title_font)
        subtitle_font = FontFactory.regular(title_font.size - 10)
        subtitle_width, subtitle_height = text_size(self.subtitle, title_font)
        box_height = title_height + subtitle_height + line_separation + 2 * v_padding

        img = Image.new('RGBA', (width, box_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # background
        bg = Image.new('RGB', (width, box_height))
        gradient(bg, direction=GradientDirection.LEFT_TO_RIGHT)
        img.paste(bg)

        # box
        draw.rectangle(((0, 0), (box_width, box_height)), fill=self.box_color)

        # Name
        padding_after_box = box_width + 20
        draw.text(
            (padding_after_box, v_padding),
            self.title.upper(),
            fill=(255, 255, 255),
            font=title_font
        )
        draw.text(
            (padding_after_box, v_padding+line_separation+title_height),
            self.subtitle,
            fill=(255, 255, 255),
            font=subtitle_font
        )

        # logo
        with Image.open(self.get_image()) as team_image:
            padding = 4
            image_size = box_height - padding
            team_image = resize(team_image, image_size, image_size)
            paste(team_image, img, left=width - team_image.width - 10)

        return img

    def get_parallelogram(self, width, height):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.polygon(
            ((0, height),
            (height, 0),
            (width, 0),
            (width-height, height)),
            self.lineup_bg_color
        )
        return img

    def get_lineup_image(self, width, height, pilots:List["Pilot"]):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # Parallelogram
        parallelogram_bottom_margin = 5
        parallelogram_height = int(.32 * height) # should be ~ 67
        parallelogram_img = self.get_parallelogram(width, parallelogram_height)
        parallelogram_pos = paste(
            parallelogram_img,
            img,
            top=height-parallelogram_height - parallelogram_bottom_margin,
            use_obj=True
        )

        remaining_height = height - parallelogram_height - parallelogram_bottom_margin
        max_logo_width = int(.3 * width) # ~240
        max_logo_height = int(.675 * remaining_height) # ~96
        # Logo
        with self.get_lineup_logo() as logo_img:
            logo_img = resize(logo_img, max_logo_width, max_logo_height)
            logo_pos = paste(logo_img, img, top=(remaining_height-max_logo_height)//2, use_obj=True)

        # FIXME refactor below + try to open only once the psd

        # Pilots
        pilot_font = FontFactory.black(30)
        # name
        left_pilot_name_img = pilots[0].get_name_image(pilot_font)
        left_pilot_name_left = parallelogram_pos.left + parallelogram_img.height + 10
        shift = 2 if '_' in pilots[0].name else 5
        left_pilot_name_top = (parallelogram_pos.top) + left_pilot_name_img.height//2 + shift
        paste(left_pilot_name_img, img, top=left_pilot_name_top, left=left_pilot_name_left)

        # img
        left_pilot_img = pilots[0].get_close_up_image()
        left_pilot_img = resize(left_pilot_img, remaining_height, remaining_height)
        left_pilot_img_left = int(((width / 2) - left_pilot_img.width) / 2)
        if not pilots[0].has_image_in_close_up_psd():
            default_img = resize(pilots[0].get_default_image(), remaining_height, remaining_height)
            default_img = default_img.crop((0,0,default_img.width,default_img.height-10))
            paste(default_img, img, top=10, left=left_pilot_img_left)
        paste(left_pilot_img, img, top=0, left=left_pilot_img_left)

        # name
        right_pilot_name_img = pilots[1].get_name_image(pilot_font)
        right_pilot_name_left = parallelogram_pos.right - parallelogram_img.height - right_pilot_name_img.width - 10
        shift = 2 if '_' in pilots[1].name else 5
        right_pilot_name_top = (parallelogram_pos.top) + right_pilot_name_img.height//2 + shift
        paste(right_pilot_name_img, img, top=right_pilot_name_top, left=right_pilot_name_left)

        # img
        right_pilot_img = pilots[1].get_close_up_image()
        right_pilot_img = resize(right_pilot_img, remaining_height, remaining_height)
        right_pilot_img_left = int((width / 2) + ((width / 2) - right_pilot_img.width) / 2)
        if not pilots[1].has_image_in_close_up_psd():
            default_img = resize(pilots[1].get_default_image(), remaining_height, remaining_height)
            default_img = default_img.crop((0,0,default_img.width,default_img.height-10))
            paste(default_img, img, top=10, left=right_pilot_img_left)
        paste(right_pilot_img, img, top=0, left=right_pilot_img_left)

        return img

    def get_box_image(self, width:int=5, height:int=30) ->PngImageFile:
        return Image.new('RGB', (width, height), self.box_color)
