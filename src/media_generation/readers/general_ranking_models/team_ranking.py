from dataclasses import dataclass
from typing import List, Tuple

import tabulate

from src.media_generation.models.team import Team
from src.media_generation.readers.general_ranking_models.ranking import Ranking, RankingRow

@dataclass
class TeamRankingRow(RankingRow):
    team_name: str = None

    # "COMPUTED"
    team: Team = None

@dataclass
class TeamRanking(Ranking):
    rows: List[TeamRankingRow] = None

    def find(self, team:Team) -> Tuple[int, TeamRankingRow]:
        for i, row in enumerate(self.rows):
            if row.team == team:
                return i+1, row
        return None, None

    def get_previous_ranking(self) -> "TeamRanking":
        out_rows = []
        last_race_index = self.amount_of_races
        if self.amount_of_races <= 1:
            return None
        for row in self.rows:
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
            out_rows.append(
                TeamRankingRow(
                    team=row.team,
                    team_name=row.team_name,
                    total_points=total_points
                )
            )
        ranking = TeamRanking(rows=out_rows)
        ranking.sort_by_points()
        return ranking

    def __str__(self):
        values = [
            [i+1, row.team.name if row.team else "No team", row.total_points]
            for i, row in enumerate(self.rows)
        ]
        return tabulate.tabulate(values, tablefmt='simple_grid')
