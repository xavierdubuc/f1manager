from typing import Dict
from ..models.enums.formula_type import FormulaType
from ..models.enums.game_mode import GameMode
from ..models.enums.gearbox import Gearbox
from ..models.enums.racing_line_mode import RacingLineMode
from ..models.enums.rule_set import RuleSet
from ..models.enums.safety_car_status import SafetyCarStatus
from ..models.enums.session_length import SessionLength
from ..models.enums.session_type import SessionType
from ..models.enums.temperature_change import TemperatureChange
from ..models.enums.track import Track
from ..models.enums.weather import Weather
from ..models.session import Session
from ..models.weather_forecast import WeatherForecast
from f1_23_telemetry.packets import PacketSessionData
from datetime import timedelta
from .abstract_manager import Change, AbstractManager


class SessionManager(AbstractManager):
    model = Session

    primitive_fields = {
        'track_temp': 'track_temperature',
        'air_temp': 'air_temperature',
        'total_laps': 'total_laps',
        'track_length': 'track_length',
        'time_of_day': 'time_of_day',
        'pit_speed_limit': 'pit_speed_limit',
        'spectator_car_index': 'spectator_car_index',
        'amount_of_pertinent_weather_forecast': 'num_weather_forecast_samples',
        'ai_difficulty': 'ai_difficulty',
        'season_identifier': 'season_link_identifier',
        'weekend_identifier': 'weekend_link_identifier',
        'session_identifier': 'session_link_identifier',
        'pit_stop_window_start_lap': 'pit_stop_window_ideal_lap',
        'pit_stop_window_end_lap': 'pit_stop_window_latest_lap',
        'pit_stop_rejoin_position': 'pit_stop_rejoin_position',
        'session_time_left':  'session_time_left',
        'session_duration': 'session_duration'
    }

    enum_fields = {
        'weather': (Weather, 'weather'),
        'session_type': (SessionType, 'session_type'),
        'track': (Track, 'track_id'),
        'formula_type': (FormulaType, 'formula'),
        'safety_car_status': (SafetyCarStatus, 'safety_car_status'),
        'gearbox': (Gearbox, 'gearbox_assist'),
        'racing_line_mode': (RacingLineMode, 'dynamic_racing_line'),
        'game_mode': (GameMode, 'game_mode'),
        'rule_set': (RuleSet, 'rule_set'),
        'session_length': (SessionLength, 'session_length'),
    }

    bool_fields = {
        'game_paused': 'game_paused',
        'is_spectating': 'is_spectating',
        'is_online': 'network_game',
        'help_steering_enabled': 'steering_assist',
        'help_braking_enabled': 'braking_assist',
        'help_pit': 'pit_assist',
        'help_pit_release': 'pit_release_assist',
        'help_ers': 'ers_assist',
        'help_drs': 'drs_assist',
        'racing_line_is_3D': 'dynamic_racing_line_type',
        'forecast_is_approximate': 'forecast_accuracy'
    }

    @classmethod
    def create(cls, packet: PacketSessionData) -> Session:
        self = super().create(packet)
        self.session_time_elapsed = timedelta(seconds=self.session_duration - self.session_time_left)
        self.weather_forecast = [
            WeatherForecast(
                session_type=SessionType(packet.weather_forecast_samples[i].session_type),
                time_offset=packet.weather_forecast_samples[i].time_offset,
                weather=Weather(packet.weather_forecast_samples[i].weather),
                track_temperature=packet.weather_forecast_samples[i].track_temperature,
                track_temperature_change=TemperatureChange(packet.weather_forecast_samples[i].track_temperature_change),
                air_temperature=packet.weather_forecast_samples[i].air_temperature,
                air_temperature_change=TemperatureChange(packet.weather_forecast_samples[i].air_temperature_change),
                rain_percentage=packet.weather_forecast_samples[i].rain_percentage
            ) for i in range(packet.num_weather_forecast_samples)
        ]
        return self

    @classmethod
    def update(cls, session: Session, packet: PacketSessionData) -> Dict[str, Change]:
        changes = super().update(session, packet)

        # computing time_elapsed field
        time_elapsed = timedelta(seconds=session.session_duration - session.session_time_left)
        if time_elapsed != session.session_time_elapsed:
            changes['session_time_elapsed'] = Change(actual=time_elapsed, old=session.session_time_elapsed)
            session.session_time_elapsed = time_elapsed

        # weather_forecast
        weather_forecast = [
            WeatherForecast(
                session_type=SessionType(packet.weather_forecast_samples[i].session_type),
                time_offset=packet.weather_forecast_samples[i].time_offset,
                weather=Weather(packet.weather_forecast_samples[i].weather),
                track_temperature=packet.weather_forecast_samples[i].track_temperature,
                track_temperature_change=TemperatureChange(packet.weather_forecast_samples[i].track_temperature_change),
                air_temperature=packet.weather_forecast_samples[i].air_temperature,
                air_temperature_change=TemperatureChange(packet.weather_forecast_samples[i].air_temperature_change),
                rain_percentage=packet.weather_forecast_samples[i].rain_percentage
            ) for i in range(packet.num_weather_forecast_samples)
        ]
        if any(map(lambda x: x[0] != x[1], zip(weather_forecast, session.weather_forecast))):
            changes['weather_forecast'] = Change(actual=weather_forecast, old=session.weather_forecast)
            session.weather_forecast = weather_forecast

        return changes
