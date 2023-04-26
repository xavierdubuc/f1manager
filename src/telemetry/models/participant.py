from dataclasses import dataclass
from .enums.team import Team
from .enums.original_driver import OriginalDriver
from .enums.nationality import Nationality


@dataclass
class Participant:
    network_id: int = None
    race_number: int = None
    name: int = None
    original_driver: OriginalDriver = None
    team: Team = None
    nationality: Nationality = None
    is_my_team_mode: bool = None
    ai_controlled: bool = None
    telemetry_is_public: bool = None

    def __str__(self):
        name = self.name.decode('utf-8') if isinstance(self.name, bytes) else self.name
        if name and name != 'Joueur':
            return name
        return f'#{self.race_number} ({self.nationality.name}) {self.team.name}'

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if self.network_id != other.network_id:
            return False
        if self.race_number != other.race_number:
            return False
        if self.name != other.name:
            return False
        if self.original_driver != other.original_driver:
            return False
        if self.team != other.team:
            return False
        if self.nationality != other.nationality:
            return False
        if self.is_my_team_mode != other.is_my_team_mode:
            return False
        if self.ai_controlled != other.ai_controlled:
            return False
        if self.telemetry_is_public != other.telemetry_is_public:
            return False
        return True
