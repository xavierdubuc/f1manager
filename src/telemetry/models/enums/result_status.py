from enum import Enum


class ResultStatus(Enum):
    invalid = 0
    inactive = 1
    active = 2
    finished = 3
    dnf = 4
    dsq = 5
    not_classified = 6
    retired = 7