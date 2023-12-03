from src.media_generation.generators.abstract_generator import AbstractGenerator
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.models.race_renderer import RaceRenderer
from src.media_generation.readers.race_reader_models.race import Race


class AbstractRaceGenerator(AbstractGenerator):
    def __init__(self, championship_config: dict, config: GeneratorConfig, season: int, identifier: str = None, *args, **kwargs):
        super().__init__(championship_config, config, season, identifier, *args, **kwargs)
        self.race: Race = self.config.race
        self.race_renderer: RaceRenderer = RaceRenderer(self.race)
