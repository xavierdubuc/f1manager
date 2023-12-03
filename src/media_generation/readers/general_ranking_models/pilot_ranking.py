from dataclasses import dataclass
from typing import List

from src.media_generation.models.pilot import Pilot
from src.media_generation.readers.general_ranking_models.ranking import Ranking, RankingRow

@dataclass
class PilotRankingRow(RankingRow):
    pilot_name: str = None
    titular: bool = True
    team_name: str = None
    mean_points: float = 0
    license_points: int = 8
    amount_of_races: int = 0

    # "COMPUTED"
    pilot: Pilot = None

@dataclass
class PilotRanking(Ranking):
    rows: List[PilotRankingRow] = None

    def sort_by_license_points(self):
        self.rows = sorted(self.rows, key=lambda row: row.license_points, reverse=True)

    def sort_by_mean_points(self):
        self.rows = sorted(self.rows, key=lambda row: row.mean_points, reverse=True)
