from dataclasses import dataclass
from src.media_generation.generators.abstract_generator import AbstractGenerator
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.helpers.transform import month_fr
from src.media_generation.models.race_renderer import RaceRenderer
from src.media_generation.readers.race_reader_models.race import Race


@dataclass
class AbstractRaceGenerator(AbstractGenerator):
    def __post_init__(self):
        super().__post_init__()
        self.race: Race = self.config.race
        self.race_renderer: RaceRenderer = RaceRenderer(self.race)

    def _get_layout_context(self):
        return dict(
            super()._get_layout_context(),
            race=self.race,
            circuit=self.race.circuit,
            circuit_country=self.race.circuit.name.upper() if self.race.circuit else "?",
            circuit_city=self.race.circuit.city.upper() if self.race.circuit else "?",
            month_fr=month_fr(self.race.full_date.month-1),
            month_fr_short=month_fr(self.race.full_date.month-1)[:3].upper(),
        )
