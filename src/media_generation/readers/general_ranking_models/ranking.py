from dataclasses import dataclass
from typing import List

from src.media_generation.readers.general_ranking_models.race_result import RaceResult

@dataclass
class RankingRow:
    total_points: float = 0
    race_results: List[RaceResult] = None

    def get_previous_ranking_row(self, points_to_remove:int, amount_race_to_withdraw:int) -> "RankingRow":
        return RankingRow()

    def should_be_ignored(self) -> bool:
        return False

@dataclass
class Ranking:
    rows: List[RankingRow] = None
    amount_of_races: int = 0

    def __post_init__(self):
        self.sort_by_points()

    def get_previous_ranking(self) -> "Ranking":
        out_rows = []
        last_race_index = self.amount_of_races
        if self.amount_of_races <= 1:
            return None
        for row in self.rows:
            if row.should_be_ignored():
                continue
            last_race_result = row.race_results[last_race_index]
            amount_race_to_withdraw = 1 if last_race_result.has_raced() else 0
            points_to_remove = last_race_result.get_points()

            # If there is a previous previous race
            # and previous race was a special format, we need to take both races into account
            if last_race_index-1 >= 0:
                before_last_race_result = row.race_results[last_race_index-1]
                if 'R' in before_last_race_result.race_number or 'S' in before_last_race_result.race_number:
                    points_to_remove += before_last_race_result.get_points()
                    amount_race_to_withdraw += (1 if before_last_race_result.has_raced() else 0)

            ranking_row = row.get_previous_ranking_row(points_to_remove, amount_race_to_withdraw)
            out_rows.append(ranking_row)
        ranking = self.__class__(rows=out_rows)
        ranking.sort_by_points()
        return ranking

    def sort_by_points(self):
        self.rows = sorted(self.rows, key=lambda row: self._get_sort_by_points_value(row), reverse=True)

    def _get_sort_by_points_value(self, row: RankingRow):
        return row.total_points

    def __iter__(self):
        return iter(self.rows)
