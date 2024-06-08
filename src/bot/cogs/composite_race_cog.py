import disnake
from disnake.ext import commands
from src.bot.cogs.ranking_cog import RankingCog
from src.bot.cogs.presences_cog import PresencesCog
from src.bot.cogs.driver_of_the_day_cog import DriverOfTheDayCog
from src.bot.cogs.results_cog import ResultsCog
from src.media_generation.helpers.generator_type import GeneratorType
from src.media_generation.readers.race_reader_models.race import RaceType
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.bot.cogs.race_cog import RACE_NUMBER_PARAM, RaceCog


class CompositeRaceCog(RaceCog):
    visual_type = 'results'

    async def _bootstrap(self, inter: disnake.ApplicationCommandInteraction, **kwargs):
        await super()._bootstrap(inter, **kwargs)
        await inter.followup.send("Ok, laissez faire Gaëtano !")

    def _get_first_and_second_race_configs(self, race_number:int, config:GeneratorConfig, championship_config: dict, season: int):
        first_race_config = config
        second_race_config = config
        first_race_number = second_race_number = race_number
        if config.race.type in (RaceType.SPRINT_1, RaceType.DOUBLE_GRID_1):
            first_race_number = race_number
            second_race_number = race_number[:-2]
            second_race_config = self._read_config(second_race_number, 'results', GeneratorType.RESULTS, championship_config, season)
        elif config.race.type in (RaceType.SPRINT_2, RaceType.DOUBLE_GRID_2):
            letter = 'S' if config.race.type == RaceType.SPRINT_2 else 'R'
            first_race_number = f'{race_number} {letter}'
            second_race_number = race_number
            first_race_config = self._read_config(first_race_number, 'results', GeneratorType.RESULTS, championship_config, season)
            second_race_config = config
        return first_race_number, first_race_config, second_race_number, second_race_config
