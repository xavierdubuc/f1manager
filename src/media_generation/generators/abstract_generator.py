from abc import ABC, abstractmethod
from ..models import Visual
from ..helpers.generator_config import GeneratorConfig
from PIL import Image
from PIL.PngImagePlugin import PngImageFile

class AbstractGenerator(ABC):
    def __init__(self, config:GeneratorConfig):
        self.config = config

    def generate(self):
        base_img = self._generate_basic_image()
        title_img = self._generate_title_image(base_img)
        if title_img:
            if title_img.mode == 'RGB':
                base_img.paste(title_img)
            else:
                base_img.paste(title_img, title_img)
        self._add_content(base_img)
        base_img.save(self.config.output, quality=95)
        return self.config.output

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        visual = Visual(self._get_visual_type(), race=self.config.race)
        width = self._get_visual_title_width(base_img)
        height = self._get_visual_title_height(base_img)
        return visual.get_title_image(width, height)

    def _generate_basic_image(self) -> PngImageFile:
        with Image.open('assets/bg.png') as bg:
            base = bg.copy().convert('RGB')
        with Image.open('assets/bgmetal.png') as gray_filter:
            gray_filter = gray_filter.copy().resize((base.width, base.height)).convert('RGBA')
        gray_filter.putalpha(150)
        base.paste(gray_filter, gray_filter)
        return base

    @abstractmethod
    def _get_visual_type(self) -> str:
        pass

    def _get_visual_title_height(self, base_img:PngImageFile = None) -> int:
        return 180

    def _get_visual_title_width(self, base_img:PngImageFile = None) -> int:
        return base_img.width

    @abstractmethod
    def _add_content(self, base_img: PngImageFile):
        pass