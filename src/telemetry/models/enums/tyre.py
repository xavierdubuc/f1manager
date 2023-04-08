from enum import Enum


class Tyre(Enum):
    none = 0
    soft = 16
    medium = 17
    hard = 18
    inter = 7
    wet = 8
    classic_dry = 9
    classic_wet = 10
    f2_wet = 15
    f2_super_soft = 19
    f2_soft = 20
    f2_medium = 21
    f2_hard = 22

    def __str__(self):
        if self == Tyre.soft:
            return 'S'
        if self == Tyre.medium:
            return 'M'
        if self == Tyre.hard:
            return 'H'
        if self == Tyre.inter:
            return 'I'
        if self == Tyre.wet:
            return 'W'
        return self.name