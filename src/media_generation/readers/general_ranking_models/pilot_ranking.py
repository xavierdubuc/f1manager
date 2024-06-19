from dataclasses import dataclass
from typing import List, Tuple

import tabulate

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

    def find(self, pilot:Pilot) -> Tuple[int, RankingRow]:
        for i, row in enumerate(self.rows):
            if row.pilot == pilot:
                return i+1, row
        return None, None

    def get_previous_ranking(self):
        out_rows = []
        last_race_index = self.amount_of_races
        for row in self.rows:
            if row.amount_of_races == 0:
                continue
            last_race_result = row.race_results[last_race_index-1]
            amount_race_to_withdraw = 1 if last_race_result.has_raced() else 0
            points_to_remove = last_race_result.get_points()

            # If there is a previous previous race
            # and previous race was a special format, we need to take both races into account
            if last_race_index-2 >= 0:
                before_last_race_result = row.race_results[last_race_index-2]
                if 'R' in before_last_race_result.race_number or 'S' in before_last_race_result.race_number:
                    points_to_remove += before_last_race_result.get_points()
                    amount_race_to_withdraw += (1 if before_last_race_result.has_raced() else 0)

            total_points = row.total_points - points_to_remove
            amount_of_races = row.amount_of_races - amount_race_to_withdraw
            mean_points = (total_points / amount_of_races) if amount_of_races > 0 else 0
            out_rows.append(
                PilotRankingRow(
                    pilot_name=row.pilot_name,
                    titular=row.titular,
                    team_name=row.team_name,
                    mean_points=mean_points,
                    license_points=row.license_points,
                    amount_of_races=amount_of_races,
                    pilot=row.pilot,
                    total_points=total_points
                )
            )
        ranking = PilotRanking(rows=out_rows)
        ranking.sort_by_points()
        return ranking

    def __str__(self):
        values = [
            [i+1, row.pilot.name, row.total_points] for i, row in enumerate(self.rows)
        ]
        return tabulate.tabulate(values, tablefmt='simple_grid')
