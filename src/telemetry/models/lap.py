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
        print('S1')
        return self._get_square(self.sector1_time_in_ms, personal_best, overall_best)

    def get_second_sector_square(self, personal_best, overall_best):
        if not self.sector1_time_in_ms or not self.sector2_time_in_ms:
            sector2_time = None
        else:
            sector2_time = (self.sector2_time_in_ms - self.sector1_time_in_ms)
        print('S2')
        return self._get_square(sector2_time, personal_best, overall_best)

    def get_third_sector_square(self, total_lap_time, personal_best, overall_best):
        if not self.sector2_time_in_ms or not total_lap_time:
            sector3_time = None
        else:
            sector3_time = (total_lap_time - self.sector2_time_in_ms)
        print('S3')
        return self._get_square(sector3_time, personal_best, overall_best)

    def _get_square(self, current_time, personal_best, overall_best):
        print(f'CURRENT: {current_time} --> PB {personal_best} / OB {overall_best}')
        if self.current_lap_invalid:
            return '🟥'
        if not current_time:
            return '🔳'
        if not overall_best or current_time < overall_best:
            return '🟪'
        elif not personal_best or current_time < personal_best:
            return '🟩'
        return '🟨'