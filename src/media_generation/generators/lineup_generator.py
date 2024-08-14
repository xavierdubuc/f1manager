from dataclasses import dataclass
from ..generators.abstract_race_generator import AbstractRaceGenerator


@dataclass
class LineupGenerator(AbstractRaceGenerator):
    visual_type: str = 'lineup'
