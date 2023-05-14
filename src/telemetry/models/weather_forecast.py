from dataclasses import dataclass

from .enums.session_type import SessionType
from .enums.temperature_change import TemperatureChange
from .enums.weather import Weather


@dataclass
class WeatherForecast:
    session_type: SessionType = None
    time_offset: int = None  # minutes
    weather: Weather = None
    track_temperature: int = None
    air_temperature :int = None
    rain_percentage: int = None
    track_temperature_change: TemperatureChange = None
    air_temperature_change: TemperatureChange = None

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if self.session_type != other.session_type:
            return False
        if self.time_offset != other.time_offset:
            return False
        if self.weather != other.weather:
            return False
        if self.track_temperature != other.track_temperature:
            return False
        if self.air_temperature != other.air_temperature:
            return False
        if self.rain_percentage != other.rain_percentage:
            return False
        if self.track_temperature_change != other.track_temperature_change:
            return False
        if self.air_temperature_change != other.air_temperature_change:
            return False
        return True

    def __str__(self):
        if self.rain_percentage < 40:
            rain_percentage_str = '💧'
        else:
            rain_percentage_str = '💦'

        time_offset = f'+ {str(self.time_offset).rjust(3)}min'
        weather = str(self.weather)
        rain = f'{rain_percentage_str}{str(self.rain_percentage).rjust(3)}%'
        track = f'Piste: {self.track_temperature}°C'
        air = f'Air: {self.air_temperature}°C'
        return f'`{time_offset}` → {weather} ← [{rain}] `{track}` ({air})'