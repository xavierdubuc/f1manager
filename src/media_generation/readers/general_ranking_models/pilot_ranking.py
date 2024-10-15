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

    def get_previous_ranking_row(self, points_to_remove:int, amount_race_to_withdraw:int) -> "PilotRankingRow":
        total_points = self.total_points - points_to_remove
        amount_of_races = self.amount_of_races - amount_race_to_withdraw
        mean_points = (total_points / amount_of_races) if amount_of_races > 0 else 0
        return PilotRankingRow(
            pilot_name=self.pilot_name,
            titular=self.titular,
            team_name=self.team_name,
            mean_points=mean_points,
            license_points=self.license_points,
            amount_of_races=amount_of_races,
            pilot=self.pilot,
            total_points=total_points
        )

    def should_be_ignored(self) -> bool:
        return self.amount_of_races == 0

@dataclass
class PilotRanking(Ranking):
    rows: List[PilotRankingRow] = None

    def sort_by_license_points(self):
        self.rows = sorted(self.rows, key=lambda row: row.license_points, reverse=True)

    def sort_by_mean_points(self):
        self.rows = sorted(self.rows, key=lambda row: row.mean_points, reverse=True)

    def find(self, pilot:Pilot) -> Tuple[int, PilotRankingRow]:
        for i, row in enumerate(self.rows):
            if row.pilot == pilot:
                return i+1, row
        return None, None

    def _get_sort_by_points_value(self, row: PilotRankingRow):
        if row.pilot.aspirant:
            second_criteria = 1
        elif row.pilot.reservist:
            second_criteria = 0
        else:
            second_criteria = 2
        # first sort by points, then titular first, then alphabetical
        return (row.total_points, second_criteria, -ord(row.pilot.name.lower()[0]))

    def __str__(self):
        values = [
            [i+1, row.pilot.name, row.total_points] for i, row in enumerate(self.rows)
        ]
        return tabulate.tabulate(values, tablefmt='simple_grid')
