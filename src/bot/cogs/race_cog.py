import logging
import disnake
from disnake.ext import commands
from src.bot.cogs.vignebot_cog import VignebotCog
from src.media_generation.helpers.renderer import Renderer
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.readers.race_reader import RaceReader
from src.media_generation.helpers.generator_type import GeneratorType
from src.bot.vignebot import Vignebot
from src.media_generation.run_config import RUN_CONFIGS


RACE_NUMBER_PARAM = commands.Param(
    name="race_number",
    description='Le numéro de la course'
)

_logger = logging.getLogger(__name__)


class RaceCog(VignebotCog):
    visual_type = None

    def __init__(self, bot: Vignebot):
        super().__init__(bot)
        self.generator_type = GeneratorType(self.visual_type)
        self.run_config = RUN_CONFIGS[self.generator_type]
        self.renderer = Renderer(self.run_config)

    async def run(self, inter: disnake.ApplicationCommandInteraction, race_number: str, **kwargs):
        await self._bootstrap(inter, race_number=race_number, **kwargs)
        championship_config, season = self._get_discord_config(inter.guild_id)
        _logger.info('Reading sheet...')
        config = self._read_config(race_number, self.visual_type, self.generator_type, championship_config, season)
        await self._run(inter.followup, race_number, championship_config, season, config)

    async def call(self, channel: disnake.TextChannel, inter: disnake.ApplicationCommandInteraction, race_number: str, **kwargs):
        self.last_inter = inter
        championship_config, season = self._get_discord_config(inter.guild_id)
        config = self._read_config(race_number, self.visual_type, self.generator_type, championship_config, season)
        await self._run(channel, race_number, championship_config, season, config)

    def _read_config(self, race_number: str, visual: str, generator_type: GeneratorType,
                     championship_config: dict, season: int) -> GeneratorConfig:
        sheet_name = f'Race {race_number}'
        return RaceReader(generator_type, championship_config,
                          season, f'output/race_{visual}.png', sheet_name).read()

    async def _run(self, channel: disnake.TextChannel, race_number: str, championship_config: dict, season: int, config: GeneratorConfig):
        title = self._get_title(race_number, championship_config, season, config)
        await self._send_generated_media(channel, race_number, championship_config, season, config, title)

    def _get_title(self, race_number: str, championship_config: dict, season: int, config: GeneratorConfig):
        return None

    async def _send_generated_media(self, channel: disnake.TextChannel, race_number: str, championship_config: dict, season: int, config: GeneratorConfig, title:str):
        _logger.info('Rendering image...')
        media_path = self.renderer.render(config, championship_config, season)
        await self._send_media(channel, media_path, msg=title)
