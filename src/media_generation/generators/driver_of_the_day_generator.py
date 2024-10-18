from dataclasses import dataclass
from src.media_generation.generators.abstract_race_generator import AbstractRaceGenerator


@dataclass
class DriverOfTheDayGenerator(AbstractRaceGenerator):
    visual_type: str = 'driver_of_the_day'
