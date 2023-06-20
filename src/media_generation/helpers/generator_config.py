from dataclasses import dataclass
import enum
from typing import Dict, List
import pandas

from src.media_generation.models import Pilot, Race
from src.media_generation.models.team import Team

class GeneratorType(enum.Enum):
    Presentation = 'presentation'
    Lineup ='lineup'
    Results = 'results'
    Fastest = 'fastest'
    TeamsRanking = 'teams_ranking'
    PilotsRanking = 'pilots_ranking'

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
    ranking: pandas.DataFrame = None
    fastest_lap: FastestLap = None
    ranking_title: str = None
    ranking_subtitle: str = None
    metric: str = 'Total'
    driver_of_the_day: str = None

