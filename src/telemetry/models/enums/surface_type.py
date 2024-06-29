from enum import Enum


class SurfaceType(Enum):
    tarmac = 0
    rumble_strip = 1  # vibreur
    concrete = 2
    rock = 3
    gravel = 4
    mud = 5
    sand = 6
    grass = 7
    water = 8
    cobblestone = 9 # pavé
    metal = 10
    ridge = 11
    other = 12

    def is_on_track(self):
        return self in (SurfaceType.concrete, SurfaceType.rumble_strip, SurfaceType.tarmac)
