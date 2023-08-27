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
