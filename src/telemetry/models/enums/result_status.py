from enum import Enum

from src.telemetry.models.participant import Participant


class ResultStatus(Enum):
    invalid = 0
    inactive = 1
    active = 2
    finished = 3
    dnf = 4
    dsq = 5
    not_classified = 6
    retired = 7

    def is_still_in_the_race(self):
        return self in (ResultStatus.inactive, ResultStatus.active)

    def get_pilot_result_str(self, pilot:Participant):
        if self == ResultStatus.finished:
            return f'🏁 **{pilot}**'
        if self == ResultStatus.dnf:
            return f'🟥 **{pilot}** a NT'
        if self == ResultStatus.dsq:
            return f'🟥 **{pilot}** a été disqualifié'
        if self == ResultStatus.retired:
            return f'🟥 **{pilot}** a abandonné'
        return None
