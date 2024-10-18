from dataclasses import dataclass

from src.media_generation.generators.abstract_race_generator import \
    AbstractRaceGenerator


@dataclass
class ResultsGenerator(AbstractRaceGenerator):
    visual_type: str = 'results'
