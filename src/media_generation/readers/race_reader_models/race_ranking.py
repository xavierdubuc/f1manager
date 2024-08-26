from dataclasses import dataclass
from typing import List

from src.media_generation.models.pilot import Pilot

@dataclass
class RaceRankingRow:
    position: int
    pilot_name: str
    split: str
    tyres: str = None
    best_lap: str = None
    points: int = None
    is_driver_of_the_day: bool = False
    has_fastest_lap: bool = False

    # COMPUTED
    pilot: Pilot = None

    @property
    def delta(self):
        if self.position == 1:
            return self.split
        if self.split in ('NT', 'DSQ'):
            return self.split
        return f"+ {self.split}"

@dataclass
class RaceRanking:
    rows: List[RaceRankingRow]

    def get(self, pilot:Pilot):
        for r in self.rows:
            if r.pilot == pilot:
                return r
        return None

    def get_fastest_lap_row(self):
        for r in self.rows:
            if r.has_fastest_lap:
                return r
        return None
