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

    def get_previous_ranking_row(self, points_to_remove:int, amount_race_to_withdraw:int) -> "TeamRankingRow":
        return TeamRankingRow(
            team=self.team,
            team_name=self.team_name,
            total_points=self.total_points - points_to_remove
        )

@dataclass
class TeamRanking(Ranking):
    rows: List[TeamRankingRow] = None

    def find(self, team:Team) -> Tuple[int, TeamRankingRow]:
        for i, row in enumerate(self.rows):
            if row.team == team:
                return i+1, row
        return None, None

    def __str__(self):
        values = [
            [i+1, row.team.name if row.team else "No team", row.total_points]
            for i, row in enumerate(self.rows)
        ]
        return tabulate.tabulate(values, tablefmt='simple_grid')
