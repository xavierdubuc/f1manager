from dataclasses import dataclass

from src.media_generation.generators.abstract_generator import AbstractGenerator


@dataclass
class SeasonPilotsGenerator(AbstractGenerator):
    visual_type: str = 'season_pilots'
