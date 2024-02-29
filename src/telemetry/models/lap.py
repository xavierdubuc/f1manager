from dataclasses import dataclass
from .enums.driver_status import DriverStatus
from .enums.pit_status import PitStatus
from .enums.result_status import ResultStatus


@dataclass
class Lap:
    last_lap_time_in_ms: int = None
    current_lap_time_in_ms: int = None
    sector_1_time_in_ms: int = None
    sector_1_time_in_minutes: int = None
    sector_2_time_in_ms: int = None
    sector_2_time_in_minutes: int = None
    delta_to_car_in_front_in_ms: int = None
    delta_to_race_leader_in_ms: int = None
    lap_distance: float = None
    total_distance: float = None
    safety_car_delta: float = None
    car_position: int = None
    current_lap_num: int = None
    num_pit_stops: int = None
    sector: int = None
    current_lap_invalid: bool = None
    penalties: int = None
    total_warnings: int = None
    corner_cutting_warnings: int = None
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

    @property
    def sector_3_time_in_ms(self):
        if not self.sector_1_time_in_ms or not self.sector_2_time_in_ms or not self.current_lap_time_in_ms:
            return None
        return (self.current_lap_time_in_ms - self.sector_2_time_in_ms - self.sector_1_time_in_ms)

    def __str__(self):
        return f'Lap {self.current_lap_num}'

    def is_leader(self):
        return self.car_position == 1

    def get_lap_num_title(self, total_amount_of_laps):
        if not total_amount_of_laps:
            return f'` TOUR {str(self.current_lap_num).rjust(2)} `'
        return f'` TOUR {str(self.current_lap_num).rjust(2)}/{total_amount_of_laps} `'

    def get_position_evolution(self, previous_lap:'Lap'):
        delta = self.car_position - previous_lap.car_position
        if delta == 0:
            return None
        actual = self.car_position
        actual_str = f'P{str(actual).rjust(2)}'
        if delta >= 1:
            return f'`{actual_str}` (🔻 {str(delta).rjust(2)})'
        else:
            return f'`{actual_str}` (⬆️ {str(-delta).rjust(2)})'

    def get_squared_repr(self, pb_sector1, ob_sector1, pb_sector2, ob_sector2, total_lap_time, pb_sector3, ob_sector3):
        s1 = self.get_first_sector_square(pb_sector1, ob_sector1)
        s2 = self.get_second_sector_square(pb_sector2, ob_sector2)
        s3 = self.get_third_sector_square(total_lap_time, pb_sector3, ob_sector3)
        return f'{s1}{s2}{s3}'

    def get_first_sector_square(self, personal_best, overall_best):
        return self._get_square(self.sector_1_time_in_ms, personal_best, overall_best)

    def get_second_sector_square(self, personal_best, overall_best):
        return self._get_square(self.sector_2_time_in_ms, personal_best, overall_best)

    def get_third_sector_square(self, total_lap_time, personal_best, overall_best):
        if not self.sector_2_time_in_ms or not total_lap_time:
            return self._get_square(None, personal_best, overall_best)
        return self._get_square(self.sector_3_time_in_ms, personal_best, overall_best)

    def _get_square(self, current_time, personal_best, overall_best):
        if self.current_lap_invalid:
            return '🟥'
        if not current_time:
            return '🔳'
        if not overall_best or current_time <= overall_best:
            return '🟪'
        elif not personal_best or current_time <= personal_best:
            return '🟩'
        return '🟨'
