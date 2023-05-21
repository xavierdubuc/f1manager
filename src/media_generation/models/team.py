from dataclasses import dataclass
from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngImageFile
from ..font_factory import FontFactory
from ..helpers.transform import *


@dataclass
class Team:
    name: str
    title: str
    subtitle: str
    main_color: str = 'white'
    secondary_color: str = 'black'
    box_color: str = 'black'
    standing_bg: str = 'black'
    standing_fg: str = 'white'
    breaking_fg_color: tuple = (255, 255, 255)
    breaking_bg_color: tuple = (255, 255, 255)
    breaking_line_color: tuple = (0, 0, 0)
    breaking_use_white_logo: bool = False
    pole_fg_color: tuple = None
    pole_bg_color: tuple = None
    pole_line_color: tuple = None

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

    def get_image(self):
        return f'assets/teams/{self.name}.png'

    def get_breaking_logo(self):
        return self.get_white_logo() if self.breaking_use_white_logo else self.get_image()

    def get_white_logo(self):
        return f'assets/teams/white/{self.name}.png'

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

    def get_lineup_image(self, width, height, pilots):
        # team
        bg_color = (30, 30, 30, 235)
        img = Image.new('RGBA', (width, height), bg_color)

        font_size = 28
        small_font_size = font_size - 8
        line_separation = font_size + 4
        box_width = 10
        box_height = font_size+line_separation

        draw = ImageDraw.Draw(img)

        big_font = FontFactory.regular(font_size+10)
        font = FontFactory.bold(font_size)
        small_font = FontFactory.regular(small_font_size)

        # box
        box_height = int(.75*height)
        box = self.get_box_image(height=box_height)
        box_pos = paste(box, img, left=0, use_obj=True)

        # logo
        image_size = int(.75*height)
        with self.get_results_logo() as team_image:
            team_image = resize(team_image, image_size, image_size)
            logo_pos = paste(team_image, img, box_pos.right + 20, use_obj=True)

        title = text(self.title.upper(), (255,255,255), font)
        subtitle = text(self.subtitle, (255,255,255), small_font)
        text_height = title.height + subtitle.height
        paste(
            title, img, left=logo_pos.right + 20,
            top=(height-text_height)//2-10,
            use_obj=True
        )
        paste(
            subtitle, img, left=logo_pos.right + 20,
            top=(height-text_height)//2 + title.height,
            use_obj=True
        )

        left = width // 3 + 20
        draw = ImageDraw.Draw(img)
        padding_top = 12
        for pilot in pilots:

            # NUMBER
            pos_left = left + (0 if len(pilot.number) == 2 else 10)
            draw.text(
                (pos_left, padding_top),
                pilot.number,
                fill=self.secondary_color,
                stroke_fill=self.main_color,
                stroke_width=2,
                font=big_font
            )

            # NAME
            left_name = 70
            draw.text(
                (left+left_name, padding_top),
                pilot.name.upper(),
                fill=(255, 255, 255),
                font=big_font
            )
            left = int(2 * (width / 3)) + 20 * 2
        return img

    def get_box_image(self, width:int=5, height:int=30) ->PngImageFile:
        return Image.new('RGB', (width, height), self.box_color)
