from dataclasses import dataclass, field
from typing import List
from .enums.result_status import ResultStatus
from .enums.tyre import Tyre
from .enums.tyre_compound import TyreCompound


@dataclass
class Classification:
    position: int = None
    grid_position: int = None
    num_laps: int = None
    points: int = None
    num_pit_stops: int = None
    total_race_time: float = None #in seconds, without penalties
    penalties_time: int = None # total amount of time in sec
    num_penalties: int = None # total amount
    num_tyre_stints: int = None
    best_lap_time_in_ms: int = None
    result_status: ResultStatus = None
    tyre_stints_actual: List[TyreCompound] = field(default_factory=list)
    tyre_stints_visual: List[Tyre] = field(default_factory=list)
    tyre_stints_end_laps: List[int] = field(default_factory=list)

    def get_race_time(self):
        return self.total_race_time + self.penalties_time
