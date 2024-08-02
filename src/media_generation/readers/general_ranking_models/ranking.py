from dataclasses import dataclass
from typing import List

from src.media_generation.readers.general_ranking_models.race_result import RaceResult

@dataclass
class RankingRow:
    total_points: float = 0
    race_results: List[RaceResult] = None

@dataclass
class Ranking:
    rows: List[RankingRow] = None
    amount_of_races: int = 0

    def __post_init__(self):
        self.sort_by_points()

    def sort_by_points(self):
        self.rows = sorted(self.rows, key=lambda row: self._get_sort_by_points_value(row), reverse=True)

    def _get_sort_by_points_value(self, row: RankingRow):
        return row.total_points

    def __iter__(self):
        return iter(self.rows)
