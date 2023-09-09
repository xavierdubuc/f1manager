from dataclasses import dataclass
from PIL.PngImagePlugin import PngImageFile
from PIL import Image, ImageDraw, ImageFont
from enum import Enum

from ..font_factory import FontFactory

@dataclass
class Dimension():
    left: int
    top: int
    right: int
    bottom: int

class GradientDirection(Enum):
    UP_TO_DOWN = -2
    DOWN_TO_UP = 0
    LEFT_TO_RIGHT = -1
    RIGHT_TO_LEFT = 1


def gradient(img: PngImageFile, direction: GradientDirection = GradientDirection.RIGHT_TO_LEFT):
    alpha = Image.linear_gradient('L').rotate(direction.value*90).resize((img.width, img.height))
    img.putalpha(alpha)
    return img

def get_round_corner_mask(img: PngImageFile, radius=50):
    mask = Image.new('1', (img.width, img.height), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle(((0,0), (mask.width, mask.height)), radius=radius, fill=1)
    return mask

def rounded_rectangle(width, height, fill, radius=50):
    img = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(((0,0), (width, height)), radius=radius, fill=fill)
    return img

def paste_rounded(bg: PngImageFile, img: PngImageFile, xy: tuple = (0, 0), radius=50):
    mask = get_round_corner_mask(img, radius)
    bg.paste(img, xy, mask)

def resize(img: PngImageFile, width:int = None, height: int = None, keep_ratio=True):
    if width is None and height is None:
        raise Exception('Please give at least width or height!')
    if keep_ratio:
        if width is None:
            width = int((height / img.height) * img.width)
        if height is None:
            height = int((width / img.width) * img.height)
        img.thumbnail((width, height), Image.Resampling.LANCZOS)
        return img.copy()
    else:
        if width is None:
            width = height
        if height is None:
            height = width
        return img.resize((width, height))

def text_size(text:str, font:ImageFont.FreeTypeFont, img:PngImageFile=None, **kwargs):
    if not img:
        img = Image.new('RGB', (5000, 5000))
    draw = ImageDraw.Draw(img)
    _,_, width, height = draw.textbbox((0,0), text, font, **kwargs)
    return width, height

def text_on_gradient(txt: str, text_color, font:ImageFont.FreeTypeFont, padding=20, stroke_width=0, stroke_fill=None, **kwargs):
    txt_img = text(txt, text_color, font, stroke_width, stroke_fill, **kwargs)
    img = Image.new('RGBA', (txt_img.width+2*padding, txt_img.height+2*padding), (0, 0, 0, 0))
    gradient(img, GradientDirection.LEFT_TO_RIGHT)
    img.alpha_composite(txt_img, (padding, padding))
    return img

def text(text:str, text_color, font:ImageFont.FreeTypeFont, stroke_width=0, stroke_fill=None, security_padding=0, **kwargs):
    width, height = text_size(text, font, stroke_width=stroke_width, **kwargs)
    img = Image.new('RGBA', (width+security_padding, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((security_padding, 0), text, text_color, font, stroke_width=stroke_width, stroke_fill=stroke_fill, **kwargs)
    return img

def rotated_text(txt_str:str, text_color, font:ImageFont.FreeTypeFont, stroke_width=0, stroke_fill=None, angle=15, **kwargs):
    txt = text(txt_str, text_color, font, stroke_width, stroke_fill)
    return txt.rotate(angle, expand=True)

def paste(img:PngImageFile, on_what:PngImageFile, left=False, top=False, with_alpha=None):
    left = left if left is not False else (on_what.width-img.width) // 2
    top = top if top is not False else (on_what.height-img.height) // 2
    if with_alpha is True or (with_alpha is None and img.mode != 'RGB'):
        on_what.paste(img, (left, top), img)
    else:
        on_what.paste(img, (left, top))
    return Dimension(left, top, left+img.width, top+img.height)

def get_max_font_size(text, width, height, Font=FontFactory.regular, initial_font_size=20):
    img = Image.new('RGB', (width, height))
    return determine_font_size(text, img, Font, initial_font_size)

def determine_font_size(text, img, Font=FontFactory.regular, initial_font_size=20):
    font_size = initial_font_size
    txt_width, txt_height = text_size(text, Font(font_size), img)
    height_offset = 10
    is_ascending = False
    while txt_width <= img.width-height_offset and txt_height <= img.height-height_offset:
        is_ascending = True
        font_size += 1
        txt_width, txt_height = text_size(text, Font(font_size), img)
    if is_ascending:
        return font_size - 1

    while txt_width >= img.width or txt_height >= img.height:
        font_size -= 1
        txt_width, txt_height = text_size(text, Font(font_size), img)
    return font_size

def draw_lines(img: PngImageFile, color:tuple, space_between_lines=7, line_width=2):
    draw = ImageDraw.Draw(img)
    for i in range(space_between_lines, img.height, space_between_lines):
        draw.line(((0, i), (i, 0)), fill=color, width=line_width)
    offset = 1+i+space_between_lines-img.height
    diff = abs(img.height-img.width)
    max_dim = img.width if img.width > img.height else img.height
    for i in range(offset+1, max_dim, space_between_lines):
        draw.line(((i, img.height), (img.width, diff+i)), fill=color, width=line_width)

def draw_lines_all(img: PngImageFile, color:tuple, space_between_lines=7, line_width=2):
    draw = ImageDraw.Draw(img)
    i = img.width
    j = img.height
    while j > 0 or i > 0:
        line_coordinates = (0 - (img.width - i), j), (i, 0 - (img.height - j))
        draw.line(line_coordinates, fill=color, width=line_width)
        j -= space_between_lines
        i -= space_between_lines

    i = space_between_lines
    j = space_between_lines
    while i < img.width or j < img.height:
        draw.line(((i, (img.height+j)), ((img.width+i), j)), fill=color, width=line_width)
        i += space_between_lines
        j += space_between_lines

def repeat_text(base: PngImageFile, color:tuple, txt: str, Font=FontFactory.regular, font_size=120, angle=15):
    img = Image.new('RGBA', (int(1.5*base.width), int(1.5*base.height)), (0,0,0,0))
    font = Font(font_size)
    current_txt = txt
    width, height = text_size(current_txt, font, img)
    while width < img.width:
        current_txt = f'{current_txt} {txt}'
        width, height = text_size(current_txt, font, img)

    # current_txt = f'{current_txt} {txt}'
    space_between_rows = -25
    vertical_amount = 1 + ((img.height+space_between_rows) // height)
    top = 0
    for i in range(vertical_amount):
        randomized_txt = f'{current_txt[i%4:]}{current_txt[:i%4]}'
        current_txt_img = text(randomized_txt, color, font)
        current_txt_pos = paste(current_txt_img, img, top=top, left=0)
        top = current_txt_pos.bottom + space_between_rows
    img = img.rotate(angle, expand=True)
    paste(img, base)

def get_ordinal_img(i: int, Font=FontFactory.regular, font_size=24, color=(255, 255, 255), sup_font_size=None):
    font = Font(font_size)
    txt = _pos_to_ordinal(i)
    txt_width, txt_height = text_size(txt, font)
    img = Image.new('RGBA', (txt_width, txt_height), (0,0,0,0))

    sup_font_size = sup_font_size or font_size-10
    sup_font = Font(sup_font_size)

    # print number
    number_img = text(str(i), color, font)
    position_pos = paste(number_img, img, left=0)

    # print ordinal
    ordinal_img = text(_pos_to_ordinal_suffix(i), color, sup_font)
    paste(ordinal_img, img, left=position_pos.right, top=0)
    return img


def _pos_to_ordinal_suffix(n):
    suffix = {1: 'ST', 2: 'ND', 3: 'RD'}.get(4 if 10 <= n % 100 < 20 else n % 10, "TH")
    return f'{suffix}'

def _pos_to_ordinal(n):
    return f'{n}{_pos_to_ordinal_suffix(n)}'

def draw_horizontal_dotted_line(img, xy, color, width=3, step=10, space=10):
    draw = ImageDraw.Draw(img)
    begin, end = xy
    x1,y = begin
    x2,_ = end

    current = x1
    while current < x2:
        origin = (current, y)
        end = (min(current+step, x2), y)
        draw.line((origin, end),color,width)
        current = current+step+space

def date_fr(date_str:str):
    mapping = {
        'Feb': 'Fév',
        'Apr': 'Avr',
        'May': 'Mai',
        'Jun': 'Juin',
        'Jul': 'Jui',
        'Aug': 'Août',
        'Dec': 'Déc'
    }
    res = date_str
    for old, new in mapping.items():
        res = res.replace(old, new)
    return res

def month_fr(month:int):
    return [
        'Janvier',
        'Février',
        'Mars',
        'Avril',
        'Mai',
        'Juin',
        'Juillet',
        'Août',
        'Septembre',
        'Octobre',
        'Novembre',
        'Décembre'
    ][month]