import logging
from dataclasses import dataclass
from models.evolving_model import EvolvingModel
from models.enums.team import Team
from models.enums.ready_status import ReadyStatus
from models.enums.nationality import Nationality

_logger = logging.getLogger(__name__)


@dataclass
class LobbyPlayer(EvolvingModel):
    car_number: int = None
    name: int = None
    ai_controlled: bool = None
    team: Team = None
    nationality: Nationality = None
    ready_status: ReadyStatus = None

    def __str__(self):
        return f'"{self.name}" (#{self.car_number}), {self.nationality.name}, driving a {self.team.name}'

    @staticmethod
    def _get_primitive_field_names():
        return {
            'car_number': 'car_number',
            'name': 'name',
        }

    @staticmethod
    def _get_enum_field_names():
        return {
            'ready_status': (ReadyStatus, 'ready_status'),
            'team': (Team,'team_id'),
            'nationality': (Nationality,'nationality'),
        }

    @staticmethod
    def _get_bool_field_names():
        return {
            'ai_controlled': 'ai_controlled',
        }