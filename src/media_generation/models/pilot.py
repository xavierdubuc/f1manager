from dataclasses import dataclass
import os
from PIL import Image, ImageDraw
from ..font_factory import FontFactory
from .team import Team
from ..helpers.transform import text, paste


@dataclass
class Pilot:
    name: str
    team: Team = None
    number: str = 'Re'
    title: str = None
    reservist: bool = False

    def get_celebrating_image(self):
        possible_img_paths = [
            f'assets/pole/celebrating/{self.name}.png',
            f'assets/pole/celebrating/{self.team.name}_default.png',
            f'assets/pilots/1080x1080/{self.name}.png',
            f'assets/pilots/real_no_bg/{self.name}.png',
            f'assets/pilots/real/{self.name}.png',
            f'assets/pilots/1080x1080/{self.team.name}_default.png',
            f'assets/team_pilots/{self.team.name}.png'
        ]
        for img_path in possible_img_paths:
            if os.path.exists(img_path):
                return img_path
        return None

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
