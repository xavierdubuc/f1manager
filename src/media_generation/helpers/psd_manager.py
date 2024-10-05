import enum
from functools import cache
import logging
import os.path
from dataclasses import dataclass
from typing import Dict, Tuple
from PIL.PngImagePlugin import PngImageFile
from PIL import Image

from psd_tools import PSDImage

from src.media_generation.helpers.transform import resize
from src.media_generation.models.pilot import Pilot
_logger = logging.getLogger(__name__)


ASSETS_PATH = 'assets/pilots'
DEFAULT_LAYER_NAME = 'default'

class CroppingZone(enum.Enum):
    FACE = (153, 180, 443, 470)
    CLOSE_UP = (75, 125, 475, 525)
    MID_RANGE = (0, 50, 700, 1000)
    LONG_RANGE = False


@cache
@dataclass
class PSDManager:
    filepath: str
    psd: PSDImage = None

    def _open_psd(self):
        if self.psd:
            return
        self.psd = PSDImage.open(self.filepath)

    def get_pilot_image(self, pilot: Pilot, width: int = None, height: int = None, cropping_zone: CroppingZone = None) -> PngImageFile:
        # Silence all warnings from PSDImage
        initial_level = logging.getLogger().getEffectiveLevel()
        logging.getLogger().setLevel(logging.ERROR)
        selectors = {
            0: {'value': pilot.psd_name, 'use_default': not self._has_image_in_assets(pilot.psd_name)},
            1: {'value': pilot.team.psd_name if pilot.team else None, 'use_default': True}
        }
        logging.getLogger().setLevel(initial_level)
        return self.get_image(selectors, width, height, cropping_zone.value)

    def get_image(self, selectors: Dict[int, str], width: int = None, height: int = None, cropping_zone: Tuple[int, int, int, int] = False):
        results = self.select_layers(selectors)
        img = self.psd.composite(layer_filter=lambda x: x.is_visible())

        # USE IMAGE FROM ASSET if needed
        for index, result in results.items():
            if not result and not selectors[index]["use_default"]:
                with Image.open(os.path.join(ASSETS_PATH, f'{selectors[index]["value"]}.png')) as asset:
                    img.paste(asset, (0,0), asset)

        # CROP
        if cropping_zone:
            img = img.crop(cropping_zone)

        # RESIZE
        if width and not height:
            height = width
        if height and not width:
            width = height
        if width and height:
            img = resize(img, width, height)

        return img

    def select_layers(self, selectors: Dict[int, Dict[str,str]]) -> Dict[int, bool]:
        self._open_psd()
        results = {}
        for index, layer_config in selectors.items():
            fallback_default_name = DEFAULT_LAYER_NAME if layer_config['use_default'] else False
            results[index] = self._select_layer(layer_config["value"], index, fallback_default_name=fallback_default_name)
        return results

    def _select_layer(self, selector: str, group_index: int = 0, use_first_as_default: bool = False, fallback_default_name:str = DEFAULT_LAYER_NAME) -> bool:
        try:
            layers = self.psd[group_index]
            layers.visible = True
        except IndexError:
            _logger.error(f'There is no "{group_index}" in following psd, face calc index is probably wrong')
            _logger.error(self.psd)
            layers = []

        default_index = 0 if use_first_as_default else -1
        found = None
        for i, layer in enumerate(layers):
            layer_name = layer.name.replace(' ', '')
            if not use_first_as_default and fallback_default_name and layer.name == fallback_default_name:
                default_index = i
            layer.visible = layer_name == selector
            if layer.visible:
                found = layer.name
        if found:
            _logger.debug(f'Using "{found}" layer')
        else:
            _logger.warning(f'No layer found for {selector}, using default one')
            if default_index >= 0:
                layers[default_index].visible = True  # enable 'default' layer

        return found

    def _has_image_in_assets(self, selector:str):
        return os.path.exists(os.path.join(ASSETS_PATH, f"{selector}.png"))
