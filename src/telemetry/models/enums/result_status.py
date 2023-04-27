from enum import Enum

from src.media_generation.models.pilot import Pilot


class ResultStatus(Enum):
    invalid = 0
    inactive = 1
    active = 2
    finished = 3
    dnf = 4
    dsq = 5
    not_classified = 6
    retired = 7

    def get_pilot_result_str(self, pilot:Pilot):
        if self == ResultStatus.finished:
            return f'🏁 **{pilot}**'
        if self == ResultStatus.dnf:
            return f'🟥 **{pilot}** a NT'
        if self == ResultStatus.dsq:
            return f'🟥 **{pilot}** a été disqualifié'
        if self == ResultStatus.retired:
            return f'🟥 **{pilot}** a abandonné'
        return None
