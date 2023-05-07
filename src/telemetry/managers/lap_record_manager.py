from typing import Dict
from .abstract_manager import AbstractManager, Change
from ..models.enums.driver_status import DriverStatus
from ..models.enums.pit_status import PitStatus
from ..models.enums.result_status import ResultStatus
from ..models.lap_record import LapRecord
from f1_22_telemetry.packets import PacketSessionHistoryData


class LapRecordManager(AbstractManager):
    model = LapRecord
    primitive_fields = {
        'best_lap_time_lap_num': 'best_lap_time_lap_num',
        'best_sector1_lap_num': 'best_sector1_lap_num',
        'best_sector2_lap_num': 'best_sector2_lap_num',
        'best_sector3_lap_num': 'best_sector3_lap_num',
    }

    @classmethod
    def create(cls, packet: PacketSessionHistoryData) -> LapRecord:
        self = super().create(packet)
        best_lap_data = packet.lap_history_data[packet.best_lap_time_lap_num]
        self.best_lap_time = best_lap_data.lap_time_in_ms

        best_sector1_data = packet.lap_history_data[packet.best_sector1_lap_num]
        self.best_sector1_time = best_sector1_data.lap_time_in_ms

        best_sector2_data = packet.lap_history_data[packet.best_sector2_lap_num]
        self.best_sector2_time = best_sector2_data.lap_time_in_ms

        best_sector3_data = packet.lap_history_data[packet.best_sector3_lap_num]
        self.best_sector3_time = best_sector3_data.lap_time_in_ms

    @classmethod
    def update(cls, lap_record, packet: PacketSessionHistoryData) -> Dict[str, Change]:
        changes = super().update(lap_record, packet)
        if 'best_lap_time_lap_num' in changes:
            best_lap_data = packet.lap_history_data[packet.best_lap_time_lap_num]
            changes['best_lap_time'] = Change(actual=best_lap_data.lap_time_in_ms, old=lap_record.best_lap_time)
            lap_record.best_lap_time = best_lap_data.lap_time_in_ms

        if 'best_sector1_time_lap_num' in changes:
            best_sector1_data = packet.lap_history_data[packet.best_sector1_time_lap_num]
            changes['best_sector1_time'] = Change(actual=best_sector1_data.lap_time_in_ms, old=lap_record.best_sector1_time)
            lap_record.best_sector1_time = best_sector1_data.lap_time_in_ms

        if 'best_sector2_time_lap_num' in changes:
            best_sector2_data = packet.lap_history_data[packet.best_sector2_time_lap_num]
            changes['best_sector2_time'] = Change(actual=best_sector2_data.lap_time_in_ms, old=lap_record.best_sector2_time)
            lap_record.best_sector2_time = best_sector2_data.lap_time_in_ms

        if 'best_sector3_time_lap_num' in changes:
            best_sector3_data = packet.lap_history_data[packet.best_sector3_time_lap_num]
            changes['best_sector3_time'] = Change(actual=best_sector3_data.lap_time_in_ms, old=lap_record.best_sector3_time)
            lap_record.best_sector3_time = best_sector3_data.lap_time_in_ms
        return changes