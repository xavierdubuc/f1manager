from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Dict, List

from src.media_generation.models.circuit import Circuit
from src.media_generation.models.pilot import Pilot
from src.media_generation.models.team import Team
from src.media_generation.readers.race_reader_models.lineup import LineUp
from src.media_generation.readers.race_reader_models.race_ranking import RaceRanking

class RaceType(Enum):
    NORMAL = 'Normale'
    DOUBLE_GRID_1 = 'Double Grid (1)'
    DOUBLE_GRID_2 = 'Double Grid (2)'
    SPRINT_1 = 'Sprint (1)'
    SPRINT_2 = 'Sprint (2)'
    FULL_LENGTH = '100 %'

@dataclass
class Race:
    # BASE INFORMATION
    round: str
    circuit: Circuit
    laps: int
    full_date: date
    day: str
    month: str
    hour: str
    presentation_text: str
    type: RaceType

    # LINE UP
    original_lineup: LineUp
    final_lineup: LineUp
    replacements: Dict[str, str]

    # CIRCUIT FASTEST LAP
    circuit_fastest_lap_time: str = None
    circuit_fastest_lap_pilot_name: str = None
    circuit_fastest_lap_season: int = None

    # RESULTS
    qualification_result: RaceRanking = None
    race_result: RaceRanking = None

    # FASTEST LAP
    fastest_lap_time: str = None
    fastest_lap_pilot_name: str = None
    fastest_lap_lap: int = None
    driver_of_the_day_name: str = None
    driver_of_the_day_percent: str = None

    # -- COMPUTED
    fastest_lap_pilot: Pilot = None
    driver_of_the_day: Pilot = None

    def get_total_length(self):
        return '{:.3f}'.format(self.laps * self.circuit.lap_length)

    def get_pilots(self, team:Team) -> List[Pilot]:
        return [pilot for pilot in self.final_lineup.pilots.values() if pilot and pilot.team == team]

    def get_pilot(self, pilot_name:str) -> Pilot:
        return self.final_lineup[pilot_name]

    def fastest_lap_point_granted(self) -> bool:
        if self.type == RaceType.SPRINT_1:
            return False
        ranking_row = self.race_result.get_fastest_lap_row()
        if not ranking_row or ranking_row.split in ('NT', 'DSQ'):
            return False
        if self.type in (RaceType.DOUBLE_GRID_1, RaceType.DOUBLE_GRID_2):
            return ranking_row.position <= 10
        return ranking_row.position <= 14
