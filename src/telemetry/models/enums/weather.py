from enum import Enum


class Weather(Enum):
    clear = 0
    light_cloud = 1
    overcast = 2
    light_rain = 3
    heavy_rain = 4
    storm = 5
    unknown = 6

    def __str__(self):
        if self == Weather.clear:
            return '☀️'
        elif self == Weather.light_cloud:
            return '🌤️'
        elif self == Weather.overcast:
            return '🌥️'
        elif self == Weather.light_rain:
            return '🌦️'
        elif self == Weather.heavy_rain:
            return '🌧️'
        elif self == Weather.storm:
            return '⛈️'
        return '?'