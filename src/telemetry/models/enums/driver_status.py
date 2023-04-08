from enum import Enum


class DriverStatus(Enum):
    in_pit = 0
    flying_lap = 1
    in_lap = 2
    out_lap = 3
    on_track = 4