from src.media_generation.generators.abstract_generator import AbstractGenerator
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.helpers.transform import month_fr
from src.media_generation.models.race_renderer import RaceRenderer
from src.media_generation.readers.race_reader_models.race import Race


class AbstractRaceGenerator(AbstractGenerator):
    def __init__(self, championship_config: dict, config: GeneratorConfig, season: int, identifier: str = None, *args, **kwargs):
        super().__init__(championship_config, config, season, identifier, *args, **kwargs)
        self.race: Race = self.config.race
        self.race_renderer: RaceRenderer = RaceRenderer(self.race)

    def _get_layout_context(self):
        return dict(
            super()._get_layout_context(),
            race=self.race,
            circuit=self.race.circuit,
            month_fr=month_fr(self.race.full_date.month-1)
        )
