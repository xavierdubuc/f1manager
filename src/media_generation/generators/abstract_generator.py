import os
from abc import ABC, abstractmethod
from ..models import Visual
from ..helpers.generator_config import GeneratorConfig
from PIL import Image
from PIL.PngImagePlugin import PngImageFile

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
        visual = Visual(self._get_visual_type(), race=self.config.race)
        width = self._get_visual_title_width(base_img)
        height = self._get_visual_title_height(base_img)
        return visual.get_title_image(width, height)

    def _generate_basic_image(self) -> PngImageFile:
        pass

    def _get_background_image(self) -> PngImageFile:
        path = os.path.join('assets/backgrounds', self.championship_config['name'], f'{self._get_visual_type()}.png')
        if os.path.exists(path):
            return Image.open(path)

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