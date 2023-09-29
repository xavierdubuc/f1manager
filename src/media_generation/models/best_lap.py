from dataclasses import dataclass

from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngImageFile
from ..helpers.transform import text, paste

from src.media_generation.font_factory import FontFactory


@dataclass
class BestLap:
    pilot_name: str = None
    lap_time: str = None
    championship_name: str = 'FBRT'
    season: int = None
