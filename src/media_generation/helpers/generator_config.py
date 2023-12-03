from dataclasses import dataclass
from typing import Dict, List
from src.media_generation.helpers.generator_type import GeneratorType

from src.media_generation.models import Pilot, Race
from src.media_generation.models.team import Team
from src.media_generation.readers.general_ranking_models.ranking import Ranking


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
    # fastest_lap: FastestLap = None
    ranking_title: str = None
    ranking_subtitle: str = None
    metric: str = 'Total'
    driver_of_the_day: str = None
    grid_positions: dict = None

    def __post_init__(self):
        if self.qualif_ranking and self.ranking:
            self._compute_grid_positions()

    def _compute_grid_positions(self):
        self.grid_positions = {}
        i = 1
        for _, line in self.qualif_ranking.iterrows():
            if line['B']:
                self.grid_positions[line['B']] = i
            i += 1