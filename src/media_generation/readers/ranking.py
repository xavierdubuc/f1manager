from dataclasses import dataclass
from typing import List

from src.media_generation.readers.race_result import RaceResult

@dataclass
class RankingRow:
    total_points: float = 0
    race_results: List[RaceResult] = None

@dataclass
class Ranking:
    rows: List[RankingRow] = None

    def __post_init__(self):
        self.sort_by_points()

    def sort_by_points(self):
        self.rows = sorted(self.rows, key=lambda row: row.total_points, reverse=True)

    def __iter__(self):
        return iter(self.rows)