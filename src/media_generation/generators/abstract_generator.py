import os
import logging
from abc import ABC

from dataclasses import dataclass

from src.media_generation.font_factory import FontFactory
from src.media_generation.helpers.layout_manager import LayoutManager
from src.media_generation.helpers.transform import Dimension, paste, resize, text
from src.media_generation.layout.layout import Layout
from ..helpers.generator_config import GeneratorConfig
from PIL import Image
from PIL.PngImagePlugin import PngImageFile


_logger = logging.getLogger(__name__)


@dataclass
class AbstractGenerator:
    championship_config: dict
    config: GeneratorConfig
    season: int
    identifier: str = None
    visual_type: str = None
    layout: Layout = None
    visual_config: dict = None

    def __post_init__(self):
        sttngs = self.championship_config['settings']
        self.visual_config = sttngs['visuals'].get(self._get_visual_type(), {})
        self.layout = LayoutManager().load(
            sttngs.get('layouts', {}).get(self._get_visual_type(), {})
        )

    def generate(self) -> str:
        if self.layout:
            _logger.info('Using layout method...')
            ctx = self._get_layout_context()
            _logger.debug(f'Available vars in context {ctx.keys()}')
            img = self.layout.render(context=ctx)
        else:
            _logger.info('Using legacy method...')
            img = self._generate_basic_image()
            title_img = self._generate_title_image(img)
            if title_img:
                if title_img.mode == 'RGB':
                    img.paste(title_img)
                else:
                    img.paste(title_img, title_img)
            self._add_content(img)
        img.save(self.config.output, quality=100)
        return self.config.output

    def _get_layout_context(self):
        return {
            'identifier': self.identifier,
            'season': self.season,
            'config': self.config,
        }

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        title_config = self.visual_config.get('title', {})
        return self._get_customized_title_image(base_img, title_config)

    def _get_customized_title_image(self,  base_img: PngImageFile, title_config: dict) -> PngImageFile:
        width = title_config.get('width', base_img.width)
        height = title_config.get('height', 180)
        if height == 0 or width == 0:
            return
        title_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        return title_img

    def _render_initial_image(self) -> PngImageFile:
        width = self.visual_config.get('width', 1920)
        height = self.visual_config.get('height', 1080)
        _logger.info(f'Output size is {width}px x {height}px')
        bgcolor = self.visual_config.get('background', (30, 30, 30))
        return Image.new('RGB', (width, height), bgcolor)

    def _generate_basic_image(self) -> PngImageFile:
        img = self._render_initial_image()
        width = self.visual_config.get('width', 1920)
        height = self.visual_config.get('height', 1080)
        bg = self._get_background_image()
        if bg:
            with bg:
                bg = bg.resize((width, height))
                if bg.mode not in ('RGB', 'RGBA'):
                    bg = bg.convert('RGB')
                paste(bg, img)
        return img

    def _get_background_image(self) -> PngImageFile:
        path = os.path.join('assets/backgrounds', self.championship_config['name'], f'{self._get_visual_type()}.png')
        if os.path.exists(path):
            return Image.open(path)

    def text(self, config: dict, content: str,
             stroke_fill=None,
             security_padding=0,
             default_font=FontFactory.black,
             default_font_size=60,
             default_color=(255, 255, 255)) -> PngImageFile:
        font_size = config.get('font_size', default_font_size)
        font_color = config.get('font_color', default_color)
        font_name = config.get('font')
        font = FontFactory.get_font(font_name, font_size, default_font)
        if sw := config.get('stroke_width', False):
            return text(content, font_color, font, stroke_fill=stroke_fill, stroke_width=sw, security_padding=security_padding or sw)
        return text(content, font_color, font)

    def paste_image_from_config(self, config: dict, img: PngImageFile) -> Dimension:
        if not config:
            return
        with Image.open(config['path']) as original:
            height = config.get('height', False)
            width = config.get('width', False)
            if width and height:
                img_to_paste = resize(original, width=width, height=height)
            elif width:
                img_to_paste = resize(original, width=width)
            elif height:
                img_to_paste = resize(original, height=height)
        return self.paste_image(img_to_paste, img, config)

    def paste_image(self, img: PngImageFile, on: PngImageFile,  config: dict) -> Dimension:
        left = config.get('left', False)
        if not left:
            right = config.get('right', False)
            if right is not False:
                left = on.width - img.width - right
        top = config.get('top', False)
        if not top:
            bottom = config.get('bottom', False)
            if bottom is not False:
                top = on.height - img.height - bottom

        return paste(img, on, left=left, top=top)

    def _render_image_from_file(self, path: str, width: int, height: int) -> PngImageFile:
        if not path:
            return None
        with Image.open(path) as original:
            img = resize(
                original,
                height=height,
                width=width,
                keep_ratio=False
            )
        return img

    def _render_position_image(self, position: int, position_config: dict = None) -> PngImageFile:
        width = position_config.get('width', 100)
        height = position_config.get('height', 100)
        position_container = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        position_img = self.text(position_config, str(position), default_font_size=70, default_color=(0, 0, 0))
        paste(position_img, position_container)
        return position_container

    def _render_progression_image(self, progression: int, prog_config: dict = None, icon_config: dict = None, text_config: dict = None) -> PngImageFile:
        icon_config = icon_config or prog_config.get('icon')
        text_config = text_config or prog_config.get('text')
        prog_img = Image.new(
            'RGB',
            (prog_config.get('width', 90), prog_config.get('height', 105)),
            prog_config.get('color', (255, 255, 255))
        )
        if not progression or progression == 0:
            prog_content = '-'
            text_config = prog_config.get('text_no_icon', text_config)
            prog_text = self.text(text_config, prog_content)
            self.paste_image(prog_text, prog_img, text_config)
        else:
            if progression > 0:
                with Image.open('assets/up.png') as icon:
                    prog_icon = resize(icon, height=icon_config.get('height'))
                prog_content = str(progression)
            elif progression < 0:
                with Image.open('assets/down.png') as icon:
                    prog_icon = resize(icon, height=icon_config.get('height'))
                prog_content = str(-progression)
            if len(prog_content) >= 2:
                text_config = prog_config.get('text_long')
                icon_config = prog_config.get('icon_long')
            self.paste_image(prog_icon, prog_img, icon_config)
            prog_text = self.text(text_config, prog_content)
            self.paste_image(prog_text, prog_img, text_config)
        return prog_img

    def _render_points_image(self, points: float, config: dict) -> PngImageFile:
        img = Image.new(
            'RGB',
            (config.get('width', 190), config.get('height', 190)),
            config.get('color', (255, 0, 0))
        )
        points_txt = self.text(config, str(points))
        paste(points_txt, img)
        return img

    def _get_visual_type(self) -> str:
        return self.visual_type

    def _get_visual_title_height(self, base_img: PngImageFile = None) -> int:
        return self.visual_config.get('title', {}).get('height', 180)

    def _get_visual_title_width(self, base_img: PngImageFile = None) -> int:
        return base_img.width

    def _add_content(self, base_img: PngImageFile):
        pass
