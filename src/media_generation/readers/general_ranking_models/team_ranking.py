from dataclasses import dataclass
from typing import List

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