from dataclasses import dataclass

from src.media_generation.generators.abstract_race_generator import \
    AbstractRaceGenerator


@dataclass
class ResultsGenerator(AbstractRaceGenerator):
    visual_type: str = 'results'

    def _get_layout_context(self):
        if not self.race.fastest_lap_pilot:
            raise ValueError("Le pilote ayant obtenu le meilleur tour n'est pas spécifié")
        return super()._get_layout_context()
