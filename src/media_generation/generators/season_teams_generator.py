from dataclasses import dataclass
from ..generators.abstract_race_generator import AbstractGenerator


@dataclass
class SeasonTeamsGenerator(AbstractGenerator):
    visual_type: str = 'season_teams'
