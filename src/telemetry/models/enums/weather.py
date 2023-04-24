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
            return 'Ensoleillé'
        elif self == Weather.light_cloud:
            return 'Légérement nuageux'
        elif self == Weather.overcast:
            return 'Couvert'
        elif self == Weather.light_rain:
            return 'Pluie fine'
        elif self == Weather.heavy_rain:
            return 'Pluie forte'
        elif self == Weather.storm:
            return 'Tempête':
        return '?'