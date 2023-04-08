from typing import Dict
from ..models.enums.nationality import Nationality
from ..models.enums.original_driver import OriginalDriver
from ..models.enums.team import Team
from ..models.participant import Participant
from .abstract_manager import AbstractManager, Change
from f1_22_telemetry.packets import PacketParticipantsData


class ParticipantManager(AbstractManager):
    model = Participant

    primitive_fields = {
        'network_id': 'network_id',
        'race_number': 'race_number',
    }

    enum_fields = {
        'original_driver': (OriginalDriver, 'driver_id'),
        'team': (Team, 'team_id'),
        'nationality': (Nationality, 'nationality'),
    }

    bool_fields = {
        'is_my_team_mode': 'my_team',
        'ai_controlled': 'ai_controlled',
        'telemetry_is_public': 'your_telemetry',
    }

    @classmethod
    def create(cls, packet: PacketParticipantsData) -> Participant:
        self = super().create(packet)
        self.name = packet.name.decode('utf-8')
        return self

    @classmethod
    def update(cls, participant: Participant, packet: PacketParticipantsData) -> Dict[str, Change]:
        changes = super().update(participant, packet)
        new_name = packet.name.decode('utf-8')
        if new_name != participant.name:
            changes['name'] = Change(old=participant.name, actual=new_name)
            participant.name = new_name

        return changes
