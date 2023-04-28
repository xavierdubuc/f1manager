import argparse
import logging
import math
from PIL import Image, ImageDraw
from src.media_generation.data import teams_idx
from src.media_generation.font_factory import FontFactory
from src.media_generation.models import Visual
from src.media_generation.helpers.transform import *


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
_logger = logging.getLogger(__name__)


class BreakingCommand(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument("main", help="Main (first) line of text")
        self.add_argument("second", help="Second line of text")
        self.add_argument("-t", "--team", help="Concerned team", dest='team', default=None)
        self.add_argument("-b", "--background", help="Background color to use (ignored if -t/--team is specified)", dest='bg', default="255,255,255")
        self.add_argument("-f", "--foreground", help="Foreground color to use (ignored if -t/--team is specified)", dest='fg', default="0,0,0")
        self.add_argument("-o", "--output", help="Output file to use", dest='output', default=None)
        self.add_argument("-i", "--input", help="Image to use as main picture", dest='input', default='assets/circuits/photos/belgium.png')
        self.add_argument('-p', '--padding-top', help="Top padding in pixel to use to align the image", dest='padding_top', default=None)

class Renderer:
    def __init__(self, main:str, second:str, team_name:str, bg:tuple, fg:tuple, output:str, input:str, padding_top:int=None):
        self.bg_color = tuple(int(a) for a in bg.split(','))
        self.fg_color = tuple(int(a) for a in fg.split(','))
        self.main = main.upper()
        self.second = second.upper()
        self.output = output
        self.input = input
        self.team = teams_idx.get(team_name)
        if self.team:
            self.bg_color = self.team.breaking_bg_color
            self.fg_color = self.team.breaking_fg_color
        self.padding_top = int(padding_top) if isinstance(padding_top, (int, str)) else False
        _logger.info(f'padding_top will be {self.padding_top}')

    def render(self):
        width = 1080
        height = 1350

        line_color = self.team.breaking_line_color if self.team else (159, 159, 159)
        final = Image.new('RGB', (width, height), self.bg_color)
        draw_lines_all(final, line_color, space_between_lines=4, line_width=2)
        top_breaking_height = 155
        bottom_message_height = 215
        space_top_middle = 30
        space_bottom_middle = 45
        middle_img_height = final.height - top_breaking_height - bottom_message_height - space_top_middle - space_bottom_middle

        top_img = self._get_top_breaking_img(width, top_breaking_height)
        top_dim = paste(top_img, final, left=0, top=0, use_obj=True)

        middle_img = self._get_middle_picture_img(width, middle_img_height)
        middle_dim = paste(middle_img, final, left=0, top=top_dim.bottom+space_top_middle, use_obj=True)

        bottom_img = self._get_bottom_message_img(width, bottom_message_height)
        paste(bottom_img, final, left=0, top=middle_dim.bottom+space_bottom_middle)

        final.save(self.output or 'breaking.png', quality=95)
        return self.output

    def _get_top_breaking_img(self, width:int, height:int):
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        left_padding = 25
        between_padding = 40
        with Visual.get_fbrt_logo(no_border=True) as logo:
            logo = resize(logo, int(0.15 * width), height)
            logo_dim = paste(logo, img, left_padding, use_obj=True, with_alpha=True)

        font = FontFactory.black(131)
        txt = text('BREAKING', self.fg_color, font)
        paste(txt, img, logo_dim.right + between_padding, use_obj=True)

        return img

    def _get_middle_picture_img(self, width:int, height:int):
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        with Image.open(self.input) as picture:
            ratio = width / picture.width
            new_height = math.ceil(ratio*picture.height)
            picture = resize(picture, width, new_height)
            paste(picture, img, left=0, top=self.padding_top)
        draw = ImageDraw.Draw(img)
        #    -------------- (0,0) (185, 0)
        #   /             |
        #  /              |
        # /               | (0, 185)
        # |               |
        # |               | (width, height - 385)
        # |              /
        # |             /
        # |            /
        # ------------- (width-385, height) (width,height)
        upper_dim = 185
        upper_triangle = [
            (0,0),
            (upper_dim, 0),
            (0, upper_dim)
        ]
        lower_dim = 385
        lower_triangle = [
            (width, height - lower_dim),
            (width, height),
            (width - lower_dim, height)
        ]
        draw.polygon(upper_triangle, (0,0,0,0))
        draw.polygon(lower_triangle, (0,0,0,0))

        if self.team:
            with Image.open(self.team.get_breaking_logo()) as team_img:
                paste(resize(team_img, 175, 175), img, width-team_img.width-30, height-team_img.height)
        return img

    def _get_bottom_message_img(self, width:int, height:int):
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        h_padding = 45
        between_padding = 25

        text_width = width-(h_padding*2)
        main_font_size = get_max_font_size(self.main, text_width,
                                           (height-between_padding) // 2, FontFactory.black, 84)
        _logger.info(f'Will use {main_font_size}pt as main font size')
        main_font = FontFactory.black(main_font_size) # TODO compute auto
        main_txt = text(self.main, self.fg_color, main_font)
        main_left = width - main_txt.width - h_padding
        main_dim = paste(main_txt, img, top=0, left=main_left, use_obj=True)

        max_size_for_second_font_size = int(0.75 * main_font_size)
        second_font_size = get_max_font_size(self.second, text_width,
                                           (height-between_padding) // 2, FontFactory.black, max_size_for_second_font_size)
        second_font_size = min(second_font_size, max_size_for_second_font_size)
        _logger.info(f'Will use {second_font_size}pt as second font size')
        second_font = FontFactory.regular(second_font_size)
        second_txt = text(self.second, self.fg_color, second_font)
        second_left = width - second_txt.width - h_padding
        paste(second_txt, img, left=second_left, top=main_dim.bottom+between_padding, use_obj=True)

        return img

####### MAIN

if __name__ == "__main__":
    args = BreakingCommand().parse_args()
    Renderer(args.main, args.second, args.team, args.bg, args.fg, args.output, args.input, args.padding_top).render()

