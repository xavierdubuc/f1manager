from dataclasses import dataclass
from typing import Dict, List, Tuple
from src.media_generation.helpers.generator_type import GeneratorType

from src.media_generation.models.pilot import Pilot
from src.media_generation.models.team import Team
from src.media_generation.readers.general_ranking_models.ranking import Ranking
from src.media_generation.readers.race_reader_models.race import Race


@dataclass
class FastestLap:
    pilot: Pilot
    lap: str = None
    time: str = None

@dataclass
class GeneratorConfig:
    type: GeneratorType
    output: str
    pilots: Dict[str, Pilot]
    teams: List[Team]
    race: Race = None
    description: str = None
    qualif_ranking: List[str] = None
    ranking: Ranking = None
    ranking_title: str = None
    ranking_subtitle: str = None
    metric: str = 'Total'

    def find_pilot(self, participant:"Participant") -> Pilot:
        for pname, p in self.pilots.items():
            if participant.has_name:
                if participant.name_str == p.name:
                    return p
            else:
                if participant.race_number.isnumeric() and int(participant.race_number) == int(p.number):
                    return p
        return None

    def get_pilots(self, team:Team) -> Tuple[Pilot, Pilot]:
        return [pilot for pilot in self.pilots.values() if pilot and pilot.team == team]
