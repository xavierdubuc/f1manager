from typing import Dict
from .abstract_manager import Change, AbstractManager
from ..models.classification import Classification
from ..models.enums.result_status import ResultStatus
from f1_23_telemetry.packets import FinalClassificationData
from ..models.enums.tyre import Tyre

from ..models.enums.tyre_compound import TyreCompound


class ClassificationManager(AbstractManager):
    model = Classification

    primitive_fields = {
        'position': 'position',
        'grid_position': 'grid_position',
        'num_laps': 'num_laps',
        'points': 'points',
        'num_pit_stops': 'num_pit_stops',
        'total_race_time': 'total_race_time',
        'penalties_time': 'penalties_time',
        'num_penalties': 'num_penalties',
        'num_tyre_stints': 'num_tyre_stints',
        'best_lap_time_in_ms': 'best_lap_time_in_ms',
    }

    enum_fields = {
        'result_status': (ResultStatus, 'result_status'),
    }

    @classmethod
    def create(cls, packet: FinalClassificationData) -> Classification:
        self = super().create(packet)
        self.tyre_stints_actual = [
            TyreCompound(packet.tyre_stints_actual[i]) for i in range(packet.num_tyre_stints)
        ]
        self.tyre_stints_visual = [
            Tyre(packet.tyre_stints_visual[i]) for i in range(packet.num_tyre_stints)
        ]
        self.tyre_stints_end_laps = [int(packet.tyre_stints_end_laps[i]) for i in range(packet.num_tyre_stints)]
        return self

    @classmethod
    def update(cls, classification: Classification, packet: FinalClassificationData) -> Dict[str, Change]:
        changes = super().update(classification, packet)

        # tyre_stints_actual
        tyre_stints_actual = [
            TyreCompound(packet.tyre_stints_actual[i]) for i in range(packet.num_tyre_stints)
        ]
        if len(tyre_stints_actual) != len(classification.tyre_stints_actual) or any(
            map(lambda x: x[0] != x[1], zip(tyre_stints_actual, classification.tyre_stints_actual))
        ):
            changes['tyre_stints_actual'] = Change(actual=tyre_stints_actual, old=classification.tyre_stints_actual)
            classification.tyre_stints_actual = tyre_stints_actual

        # tyre_stints_visual
        tyre_stints_visual = [
            Tyre(packet.tyre_stints_visual[i]) for i in range(packet.num_tyre_stints)
        ]
        if len(tyre_stints_visual) != len(classification.tyre_stints_visual) or any(
            map(lambda x: x[0] != x[1], zip(tyre_stints_visual, classification.tyre_stints_visual))
        ):
            changes['tyre_stints_visual'] = Change(actual=tyre_stints_visual, old=classification.tyre_stints_visual)
            classification.tyre_stints_visual = tyre_stints_visual

        # tyre_stints_end_laps
        tyre_stints_end_laps = [
            int(packet.tyre_stints_end_laps[i]) for i in range(packet.num_tyre_stints)
        ]
        if len(tyre_stints_end_laps) != len(classification.tyre_stints_end_laps) or any(
            map(lambda x: x[0] != x[1], zip(tyre_stints_end_laps, classification.tyre_stints_end_laps))
        ):
            changes['tyre_stints_end_laps'] = Change(
                actual=tyre_stints_end_laps, old=classification.tyre_stints_end_laps)
            classification.tyre_stints_end_laps = tyre_stints_end_laps

        return changes
