from dataclasses import dataclass
from typing import Dict, Type
from src.media_generation.generators.abstract_generator import AbstractGenerator
from src.media_generation.generators.calendar_generator import CalendarGenerator
from src.media_generation.generators.driver_of_the_day_generator import DriverOfTheDayGenerator
from src.media_generation.generators.license_points_generator import LicensePointsGenerator
from src.media_generation.generators.lineups_generator import LineupGenerator
from src.media_generation.generators.numbers_generator import NumbersGenerator
from src.media_generation.generators.pilot_generator import PilotGenerator
from src.media_generation.generators.pilots_ranking_generator import PilotsRankingGenerator
from src.media_generation.generators.pole_generator import PoleGenerator
from src.media_generation.generators.presentation_generator import PresentationGenerator
from src.media_generation.generators.results_generator import ResultsGenerator
from src.media_generation.generators.season_lineup_generator import SeasonLineupGenerator
from src.media_generation.generators.season_ranking_generator import SeasonRankingGenerator
from src.media_generation.generators.teams_ranking_generator import TeamsRankingGenerator
from src.media_generation.helpers.generator_type import GeneratorType
from src.media_generation.helpers.reader import Reader as DefaultReader
from src.media_generation.readers.calendar_reader import CalendarReader
from src.media_generation.readers.general_ranking_reader import GeneralRankingReader
from src.media_generation.readers.race_reader import RaceReader
from src.media_generation.readers.season_ranking_reader import SeasonRankingReader

@dataclass
class RunConfig:
    Generator:Type[AbstractGenerator]
    Reader:Type[DefaultReader] = DefaultReader

@dataclass
class RaceRunConfig(RunConfig):
    Reader:Type[DefaultReader] = RaceReader

@dataclass
class GeneralRunConfig(RunConfig):
    Reader:Type[DefaultReader] = GeneralRankingReader

RUN_CONFIGS: Dict[GeneratorType, RunConfig] = {
    # RACE
    GeneratorType.LINEUP: RaceRunConfig(
        Generator=LineupGenerator
    ),
    GeneratorType.PRESENTATION: RaceRunConfig(
        Generator=PresentationGenerator
    ),
    GeneratorType.RESULTS: RaceRunConfig(
        Generator=ResultsGenerator
    ),
    GeneratorType.POLE: RaceRunConfig(
        Generator=PoleGenerator
    ),
    GeneratorType.GRID: RaceRunConfig(
        Generator={
            'package': 'src.media_generation.generators.grid_ribbon_generator',
            'name': 'GridRibbonGenerator'
        }
    ), # it cannot be included directly as it will make things fail if moviepy is not available
    GeneratorType.DRIVER_OF_THE_DAY: RaceRunConfig(
        Generator=DriverOfTheDayGenerator
    ),

    # GENERAL 
    GeneratorType.TEAMS_RANKING: GeneralRunConfig(
        Generator=TeamsRankingGenerator
    ),
    GeneratorType.PILOTS_RANKING: GeneralRunConfig(
        Generator=PilotsRankingGenerator
    ),
    GeneratorType.LICENSE_POINTS: GeneralRunConfig(
        Generator=LicensePointsGenerator
    ),

    # ONLY NEED _values SHEET
    GeneratorType.NUMBERS : RunConfig(
        Generator=NumbersGenerator
    ),
    GeneratorType.SEASON_LINEUP : RunConfig(
        Generator=SeasonLineupGenerator
    ),
    GeneratorType.PILOT : RunConfig(
        Generator=PilotGenerator
    ),

    # ALL RACES
    GeneratorType.CALENDAR: RunConfig(
        Generator=CalendarGenerator,
        Reader=CalendarReader
    ),
    GeneratorType.SEASON_RANKING: RunConfig(
        Generator=SeasonRankingGenerator,
        Reader=SeasonRankingReader
    ),
}