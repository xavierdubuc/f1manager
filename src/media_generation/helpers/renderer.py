import importlib
from src.media_generation.generators.driver_of_the_day_generator import DriverOfTheDayGenerator
from src.media_generation.generators.license_points_generator import LicensePointsGenerator

from src.media_generation.generators.pilot_generator import PilotGenerator
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
        'license_points': LicensePointsGenerator,
        'numbers': NumbersGenerator,
        'season_lineup': SeasonLineupGenerator,
        'calendar': CalendarGenerator,
        'pilot': PilotGenerator,
        'driver_of_the_day': DriverOfTheDayGenerator,
        'grid_ribbon': {
            'package': 'src.media_generation.generators.grid_ribbon_generator',
            'name': 'GridRibbonGenerator'
        }, # it cannot be included directly as it will make things fail if moviepy is not available
    }

    @classmethod
    def render(cls, config: GeneratorConfig, championship_config: dict, season:int, identifier: str = None, *args, **kwargs):
        visuals_config = championship_config['settings']['visuals']
        custom_generator = visuals_config.get(config.type, {}).get('generator')
        if custom_generator:
            generator_module = importlib.import_module(custom_generator['package'])
            generator_cls = getattr(generator_module, custom_generator['name'])
        else:
            if not config.type in cls.generators:
                raise Exception(f'Please specify a valid visual type ({", ".join(cls.generators.keys())})')
            generator_cls = cls.generators[config.type]
            if isinstance(generator_cls,dict):
                generator_module = importlib.import_module(generator_cls['package'])
                generator_cls = getattr(generator_module, generator_cls['name'])
        generator = generator_cls(championship_config, config, season, identifier, *args, **kwargs)
        return generator.generate()
