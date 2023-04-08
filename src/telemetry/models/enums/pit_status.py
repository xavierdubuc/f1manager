from enum import Enum


class PitStatus(Enum):
    not_in_pit = 0
    pitting = 1
    in_pit = 2