from dataclasses import dataclass
from datetime import timedelta
from typing import List

from src.telemetry.models.lap_record import LapRecord

from .classification import Classification
from .damage import Damage
from .enums.result_status import ResultStatus
from .enums.session_type import SessionType
from .enums.tyre import Tyre
from .enums.weather import Weather
from .enums.track import Track
from .enums.formula_type import FormulaType
from .enums.gearbox import Gearbox
from .enums.racing_line_mode import RacingLineMode
from .enums.game_mode import GameMode
from .enums.rule_set import RuleSet
from .enums.session_length import SessionLength
from .enums.safety_car_status import SafetyCarStatus
from .participant import Participant
from .telemetry import Telemetry
from .lap import Lap


@dataclass
class Session:
    # Identifier fields
    session_type: SessionType = None
    formula_type: FormulaType = None
    track: Track = None
    game_mode: GameMode = None
    session_length: SessionLength = None
    session_duration: int = None  # seconds
    weather: Weather = None

    # Other packet fields
    track_temp: int = None
    air_temp: int = None
    total_laps: int = None
    track_length: int = None
    session_time_left: int = None  # seconds
    pit_speed_limit: int = None
    game_paused: bool = None
    is_spectating: bool = None
    spectator_car_index: int = None
    safety_car_status: SafetyCarStatus = None
    is_online: bool = None
    amount_of_pertinent_weather_forecast: int = None
    weather_forecast: list = None
    forecast_accuracy_is_perfect: bool = None
    ai_difficulty: int = None
    season_identifier: int = None
    weekend_identifier: int = None
    session_identifier: int = None
    pit_stop_window_start_lap: int = None
    pit_stop_window_end_lap: int = None
    pit_stop_rejoin_position: int = None
    gearbox: Gearbox = None
    help_steering_enabled: bool = None
    help_braking_enabled: bool = None
    help_pit: bool = None
    help_pit_release: bool = None
    help_ers: bool = None
    help_drs: bool = None
    racing_line_mode: RacingLineMode = None
    racing_line_is_3D: bool = None
    rule_set: RuleSet = None
    time_of_day: int = None
    session_time_elapsed: int = 0

    # data not from packets
    participants: List[Participant] = None
    final_classification: List[Classification] = None
    damages: List[Damage] = None
    telemetries: List[Telemetry] = None
    laps: List[List[Lap]] = None
    lap_state_last_start_of_lap: List[Lap] = None
    lap_records: List[LapRecord] = None
    current_fastest_lap: int = None # in ms
    current_fastest_sector1: int = None # in ms
    current_fastest_sector2: int = None # in ms
    current_fastest_sector3: int = None # in ms

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if self.session_type != other.session_type:
            return False
        if self.track != other.track:
            return False
        if self.game_mode != other.game_mode:
            return False
        if self.session_length != other.session_length:
            return False
        return True

    def get_current_lap(self, participant:Participant) -> Lap:
        index = self.participants.index(participant)
        return self.laps[index][-1]

    def get_participant_status(self, participant:Participant) -> ResultStatus:
        lap = self.get_current_lap(participant)
        return lap.result_status

    def get_formatted_final_ranking(self, delta_char='+'):
        if not self.final_classification:
            return []
        data = []
        first_pos_time = None
        delta_column_index = 2 if self.session_type.is_race() else 3
        for participant, classification in zip(self.participants, self.final_classification):
            row = self._get_formatted_final_ranking_row(classification, participant)
            if classification.position == 1:
                first_pos_time = row[delta_column_index]
            data.append(row)

        # transform race time or fastest laps in delta
        for row in data:
            if row[0] == 1:
                row[delta_column_index] = self._format_time(row[delta_column_index])
            elif type(row[delta_column_index]) == int:
                lap_str = 'tour' if row[delta_column_index] == 1 else 'tours'
                row[delta_column_index] = f'{delta_char} {row[delta_column_index]} {lap_str}'
            elif type(row[delta_column_index]) != str:
                if row[delta_column_index]:
                    row[delta_column_index] = f'{delta_char} {self._format_time(row[delta_column_index] - first_pos_time)}'
                else:
                    row[delta_column_index] = '-' if self.session_type.is_race() else '--:--.---'

        data.sort(key=lambda x: x[0])
        return data

    def _get_formatted_final_ranking_row(self, classification:Classification, participant:Participant):
        best_lap_time = timedelta(seconds=classification.best_lap_time_in_ms/1000)
        driver = str(participant)
        if self.session_type.is_race():
            current_tyres = ''.join([str(t) for t in classification.tyre_stints_visual])
            if classification.result_status in (ResultStatus.retired, ResultStatus.dnf, ResultStatus.not_classified):
                race_time = 'NT'
            elif classification.result_status == ResultStatus.dsq:
                race_time = 'DSQ'
            elif classification.num_laps != self.total_laps:
                race_time = self.total_laps - classification.num_laps
            else:
                race_time = timedelta(seconds=classification.get_race_time())
            return [
                classification.position, driver, race_time, current_tyres, self._format_time(best_lap_time)
            ]
        else:
            return [classification.position, driver, self._format_time(best_lap_time), best_lap_time]

    def _format_time(self, obj:timedelta):
        if obj == timedelta(0):
            return '--:--.---'
        minutes = obj.seconds//60
        minutes_str = f'{obj.seconds//60}:' if minutes > 0 else ''
        seconds = obj.seconds%60
        seconds_str = str(seconds).zfill(2) if minutes > 0 else seconds
        return f'{minutes_str}{seconds_str}.{str(obj.microseconds//1000).zfill(3)}'
