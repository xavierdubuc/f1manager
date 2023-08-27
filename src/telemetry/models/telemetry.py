from dataclasses import dataclass
from typing import List

from src.telemetry.models.enums.surface_type import SurfaceType


@dataclass
class Telemetry:
    speed: int = None
    throttle: float = None
    steer: float = None
    brake: float = None
    gear: int = None
    engine_rpm: int = None
    drs: bool = None
    rev_lights_percent: int = None
    rev_lights_bit_value: int = None
    engine_temperature: int = None
    brakes_temperature: List[int] = None
    tyres_surface_temperature: List[int] = None
    tyres_inner_temperature: List[int] = None
    tyres_pressure: List[float] = None
    surface_types: List[SurfaceType] = None
