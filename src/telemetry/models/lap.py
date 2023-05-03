from dataclasses import dataclass
from .enums.driver_status import DriverStatus
from .enums.pit_status import PitStatus
from .enums.result_status import ResultStatus


@dataclass
class Lap:
    last_lap_time_in_ms: int = None
    current_lap_time_in_ms: int = None
    sector1_time_in_ms: int = None
    sector2_time_in_ms: int = None
    lap_distance: float = None
    total_distance: float = None
    safety_car_delta: float = None
    car_position: int = None
    current_lap_num: int = None
    num_pit_stops: int = None
    sector: int = None
    current_lap_invalid: bool = None
    penalties: int = None
    warnings: int = None
    num_unserved_drive_through_pens: int = None
    num_unserved_stop_go_pens: int = None
    grid_position: int = None
    driver_status: DriverStatus = None
    result_status: ResultStatus = None
    pit_status: PitStatus = None
    pit_lane_timer_active: bool = None
    pit_stop_timer_in_ms: int = None
    pit_lane_time_in_lane_in_ms: int = None
    pit_stop_should_serve_pen: int = None

    # data not from packets
    index: int = None

    def __str__(self):
        return f'Lap {self.current_lap_num}'

    def get_lap_num_title(self):
        return f'` TOUR {str(self.current_lap_num).ljust(2)} `'

    def get_position_evolution(self, previous_lap:'Lap'):
        delta = self.car_position - previous_lap.car_position
        if delta == 0:
            return None
        actual = self.car_position
        actual_str = f'P{str(actual).ljust(2)}'
        if delta >= 1:
            return f'`{actual_str}` (🔻 {str(delta).ljust(2)})'
        else:
            return f'`{actual_str}` (⬆️ {str(-delta).ljust(2)})'