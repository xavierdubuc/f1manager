from enum import Enum


class ReadyStatus(Enum):
    not_ready = 0
    ready = 1
    spectator = 2