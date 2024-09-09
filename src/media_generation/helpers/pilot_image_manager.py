from dataclasses import dataclass
from functools import cache

from src.media_generation.helpers.psd_manager import CroppingZone, PSDManager
from src.media_generation.models.pilot import Pilot

@cache
class PilotImageManager:
    def __init__(self) -> None:
        self.psd_manager: PSDManager = None

    def get_face_image(self, pilot: Pilot, width: int = None, height: int = None):
        return self.psd_manager.get_pilot_image(pilot, width, height, CroppingZone.FACE)

    def get_close_up_image(self, pilot: Pilot, width: int = None, height: int = None):
        return self.psd_manager.get_pilot_image(pilot, width, height, CroppingZone.CLOSE_UP)

    def get_mid_range_image(self, pilot: Pilot, width: int = None, height: int = None):
        return self.psd_manager.get_pilot_image(pilot, width, height, CroppingZone.MID_RANGE)

    def get_long_range_image(self, pilot: Pilot, width: int = None, height: int = None):
        return self.psd_manager.get_pilot_image(pilot, width, height, CroppingZone.LONG_RANGE)
