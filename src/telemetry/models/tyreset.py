from dataclasses import dataclass

from src.telemetry.models.enums.session_type import SessionType
from src.telemetry.models.enums.tyre import Tyre
from src.telemetry.models.enums.tyre_compound import TyreCompound


@dataclass
class TyreSet:
    actual_tyre_compound: TyreCompound = None
    visual_tyre_compound: Tyre = None
    recommended_session: SessionType = None
    wear: int = None
    life_span: int = None
    usable_life: int = None
    lap_delta_time: int = None
    available: bool = None
    fitted: bool = None
