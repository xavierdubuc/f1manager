import argparse
import logging
import textwrap
import math
from PIL import Image
from src.media_generation.data import teams_idx
from src.media_generation.font_factory import FontFactory
from src.media_generation.helpers.transform import *


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
_logger = logging.getLogger(__name__)


class QuoteCommand(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument("author", help="Auteur")
        self.add_argument("quote", help="Texte")
        self.add_argument("-t", "--team", help="Concerned team", dest='team', default=None)
        self.add_argument("-b", "--background", help="Background color to use (ignored if -t/--team is specified)", dest='bg', default="255,255,255")
        self.add_argument("-f", "--foreground", help="Foreground color to use (ignored if -t/--team is specified)", dest='fg', default="0,0,0")
        self.add_argument("-o", "--output", help="Output file to use", dest='output', default=None)
        self.add_argument("-i", "--input", help="Image to use as main picture", dest='input', default='assets/circuits/photos/belgium.png')
        self.add_argument('-p', '--padding-top', help="Top padding in pixel to use to align the image", dest='padding_top', default=None)

class Renderer:
    def __init__(self, quote:str, author:str, team_name:str, bg:tuple, fg:tuple, output:str, input:str, padding_top:int=None):
        self.bg_color = tuple(int(a) for a in bg.split(','))
        self.fg_color = tuple(int(a) for a in fg.split(','))
        self.quote = quote.upper()
        self.author = author.upper()
        self.output = output
        self.input = input
        self.team = teams_idx.get(team_name)
        if self.team:
            self.bg_color = self.team.breaking_bg_color
            self.fg_color = self.team.breaking_fg_color
        self.padding_top = int(padding_top) if isinstance(padding_top, (int, str)) else False
        _logger.info(f'padding_top will be {self.padding_top}')

    def render(self):
        with Image.open('assets/quote_bg.png') as bg:
            overlay = bg.copy()

        line_color = self.team.breaking_line_color if self.team else (159, 159, 159)
        final = Image.new('RGB', (overlay.width, overlay.height), self.bg_color)
        draw_lines_all(final, line_color, space_between_lines=4, line_width=2)

        horizontal_space = 32
        top_padding = 30
        bottom_padding = 46
        main_width = final.width - horizontal_space * 2
        main_height = final.height - top_padding - bottom_padding
        with Image.open(self.input) as picture:
            picture = resize(picture, main_width, main_height)
            blackbg = Image.new('RGB', (main_width, main_height), (20,20,20))
            gradient(blackbg, GradientDirection.DOWN_TO_UP)

        paste(picture, final, top=top_padding)
        paste(blackbg, final, top=top_padding)
        paste(overlay, final)

        # author_font_size = get_max_font_size(self.author, main_width, 44, FontFactory.black, 84)
        author_font_size = 46
        author_img = self._get_author_img(author_font_size)
        author_padding_bottom = 60
        author_position = paste(author_img, final, top=main_height-author_img.height-author_padding_bottom, use_obj=True)

        # quote_font_size = math.ceil(1.1 * author_font_size)
        quote_font_size = 51
        text_lines = textwrap.wrap(self.quote, width=29)
        padding_between = 15
        bottom = author_position.top - padding_between * 4
        text_lines.reverse()
        for text_line in text_lines:
            img = text(text_line, self.fg_color, FontFactory.bold(quote_font_size))
            pos = paste(img, final, top = bottom - img.height, use_obj=True)
            bottom = pos.top - padding_between

        final.save(self.output or 'quote.png', quality=95)
        return self.output

    def _get_author_img(self, author_font_size):
        _logger.info(f'Will use {author_font_size}pt as author font size')
        author_font = FontFactory.black(author_font_size) # TODO compute auto
        return text(self.author, self.fg_color, author_font, security_padding=5)

####### MAIN

if __name__ == "__main__":
    args = QuoteCommand().parse_args()
    Renderer(args.quote, args.author, args.team, args.bg, args.fg, args.output, args.input, args.padding_top).render()

