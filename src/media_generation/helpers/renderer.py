from src.media_generation.generators.grid_ribbon_generator import GridRibbonGenerator
from .generator_config import GeneratorConfig

from ..generators.pole_generator import PoleGenerator
from ..generators.results_generator import ResultsGenerator
from ..generators.fastest_generator import FastestGenerator
from ..generators.lineups_generator import LineupGenerator
from ..generators.presentation_generator import PresentationGenerator
from ..generators.teams_ranking_generator import TeamsRankingGenerator
from ..generators.pilots_ranking_generator import PilotsRankingGenerator
from ..generators.numbers_generator import NumbersGenerator
from ..generators.calendar_generator import CalendarGenerator
from ..generators.season_lineup_generator import SeasonLineupGenerator


class Renderer:
    generators = {
        'lineup': LineupGenerator,
        'presentation': PresentationGenerator,
        'results': ResultsGenerator,
        'fastest': FastestGenerator,
        'pole': PoleGenerator,
        'teams_ranking': TeamsRankingGenerator,
        'pilots_ranking': PilotsRankingGenerator,
        'numbers': NumbersGenerator,
        'season_lineup': SeasonLineupGenerator,
        'calendar': CalendarGenerator,
        'grid_ribbon': GridRibbonGenerator
    }

    @classmethod
    def render(cls, config: GeneratorConfig, championship_config: dict, season:int):
        if not config.type in cls.generators:
            raise Exception(f'Please specify a valid visual type ({", ".join(cls.generators.keys())})')

        generator = cls.generators[config.type](championship_config, config, season)
        return generator.generate()
