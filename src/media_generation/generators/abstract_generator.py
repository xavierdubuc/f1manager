import os
import logging
from abc import ABC, abstractmethod

from src.media_generation.helpers.transform import draw_lines_all, paste
from ..models import Visual
from ..helpers.generator_config import GeneratorConfig
from PIL import Image
from PIL.PngImagePlugin import PngImageFile


_logger = logging.getLogger(__name__)

class AbstractGenerator(ABC):
    def __init__(self, championship_config: dict, config:GeneratorConfig, season: int, identifier: str = None, *args, **kwargs):
        self.championship_config = championship_config
        self.config = config
        self.season = season
        self.visual_config = self.championship_config['settings']['visuals'].get(self._get_visual_type(), {})
        self.identifier = identifier

    def generate(self):
        base_img = self._generate_basic_image()
        title_img = self._generate_title_image(base_img)
        if title_img:
            if title_img.mode == 'RGB':
                base_img.paste(title_img)
            else:
                base_img.paste(title_img, title_img)
        self._add_content(base_img)
        base_img.save(self.config.output, quality=100)
        return self.config.output

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        title_config = self.visual_config.get('title', {})
        if title_config.get('use_legacy', False):
            visual = Visual(self._get_visual_type(), race=self.config.race)
            width = self._get_visual_title_width(base_img)
            height = self._get_visual_title_height(base_img)
            return visual.get_title_image(width, height)
        else:
            return self._get_customized_title_image(base_img, title_config)

    def _get_customized_title_image(self,  base_img: PngImageFile, title_config:dict) -> PngImageFile:
        width = title_config.get('width', base_img.width)
        height = title_config.get('height', 180)
        if height == 0 or width == 0:
            return
        title_img = Image.new('RGBA', (width, height), (0,0,0,0))
        return title_img

    def _generate_basic_image(self) -> PngImageFile:
        width = self.visual_config['width']
        height = self.visual_config['height']
        _logger.info(f'Output size is {width}px x {height}px')
        bgcolor = self.visual_config.get('background', (30, 30, 30))
        img = Image.new('RGB', (width, height), bgcolor)
        bg = self._get_background_image()
        if bg:
            with bg:
                bg = bg.resize((width, height))
                paste(bg.convert('RGB'), img)

        lines_config = self.visual_config.get('lines', {})
        if lines_config.get('enabled', False):
            draw_lines_all(img, lines_config['color'], space_between_lines=lines_config['space'], line_width=lines_config['width'])
        return img

    def _get_background_image(self) -> PngImageFile:
        path = os.path.join('assets/backgrounds', self.championship_config['name'], f'{self._get_visual_type()}.png')
        if os.path.exists(path):
            return Image.open(path)

    @abstractmethod
    def _get_visual_type(self) -> str:
        pass

    def _get_visual_title_height(self, base_img: PngImageFile = None) -> int:
        return self.visual_config.get('title', {}).get('height', 180)

    def _get_visual_title_width(self, base_img:PngImageFile = None) -> int:
        return base_img.width

    @abstractmethod
    def _add_content(self, base_img: PngImageFile):
        pass
