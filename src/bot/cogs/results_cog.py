import disnake
from disnake.ext import commands
from src.media_generation.readers.race_reader_models.race import RaceType
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.bot.cogs.race_cog import RACE_NUMBER_PARAM, RaceCog

# TODO add a param to specify provisional or not

class ResultsCog(RaceCog):
    visual_type = 'results'


    @commands.slash_command(name="resultats", description='Résultats de la course désirée')
    async def run(self, inter: disnake.ApplicationCommandInteraction,
                  race_number: str = RACE_NUMBER_PARAM, **kwargs):
        await super().run(inter, race_number, **kwargs)

    async def _run(self, channel: disnake.TextChannel, race_number: str, championship_config: dict, season: int, config: GeneratorConfig, is_provisional: bool = False):
        title = self._get_title(race_number, championship_config, season, config, is_provisional)
        await self._send_generated_media(channel, race_number, championship_config, season, config, title)

    def _get_title(self, race_number: str, championship_config: dict, season: int, config: GeneratorConfig, is_provisional: bool = False):
        final_str = '' if not is_provisional else ' (provisoires)'
        suffix = ''
        if config.race.type == RaceType.SPRINT_1:
            suffix = ' (Sprint)'
        elif config.race.type == RaceType.SPRINT_2:
            suffix = ' (Principale)'
        if config.race.type == RaceType.DOUBLE_GRID_1:
            suffix = ' (Première)'
        elif config.race.type == RaceType.DOUBLE_GRID_2:
            suffix = ' (Inversée)'
        return f'# Résultats{final_str} Course {config.race.round}{suffix} {config.race.circuit.emoji}'
