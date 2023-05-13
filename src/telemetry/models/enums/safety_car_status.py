from enum import Enum


class SafetyCarStatus(Enum):
    no = 0
    full = 1
    virtual = 2
    formation_lap = 3

    def __str__(self):
        circle = self._get_circle()
        txt = self._get_text()
        length = len(txt) + 2
        return '\n'.join(
            circle * length,
            f'{circle}{txt}{circle}',
            circle * length
        )

    def _get_circle(self):
        if self == SafetyCarStatus.no:
            return '🟢'
        if self == SafetyCarStatus.full:
            return '🔴'
        if self == SafetyCarStatus.virtual:
            return '🟡'
        return '⚪'

    def _get_text(self):
        if self == SafetyCarStatus.no:
            return '🟢 `DRAPEAU VERT` 🟢'
        if self == SafetyCarStatus.full:
            return '⛔ `FULL SAFETY CAR` ⛔'
        if self == SafetyCarStatus.virtual:
            return '⚠️ `VIRTUAL SAFETY CAR` ⚠️'
        return '🟡 `FORMATION LAP` 🟡'