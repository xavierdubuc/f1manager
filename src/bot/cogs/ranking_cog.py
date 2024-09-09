import asyncio
import logging
import disnake
from disnake.ext import commands
from src.media_generation.readers.general_ranking_reader import GeneralRankingReader
from src.bot.cogs.vignebot_cog import VignebotCog
from src.media_generation.helpers.renderer import Renderer
from src.media_generation.helpers.generator_type import GeneratorType
from src.bot.vignebot import Vignebot
from src.media_generation.run_config import RUN_CONFIGS

_logger = logging.getLogger(__name__)


class RankingCog(VignebotCog):
    last_inter: disnake.ApplicationCommandInteraction = None

    @commands.slash_command(name="classement")
    async def root(self, inter: disnake.ApplicationCommandInteraction, **kwargs):
        await self._bootstrap(inter, **kwargs)
        pass

    @root.sub_command(name="pilotes", description='Classement pilotes')
    async def pilots_command(self, inter: disnake.ApplicationCommandInteraction, **kwargs):
        championship_config, season = self._get_discord_config(self.last_inter.guild_id)
        await self.pilots(inter.followup, championship_config, season)

    @root.sub_command(name="equipes", description='Classement équipes')
    async def teams_command(self, inter: disnake.ApplicationCommandInteraction, **kwargs):
        championship_config, season = self._get_discord_config(self.last_inter.guild_id)
        await self.teams(inter.followup, championship_config, season)

    @root.sub_command(name="permis", description='Classement permis')
    async def licenses_command(self, inter: disnake.ApplicationCommandInteraction, **kwargs):
        championship_config, season = self._get_discord_config(self.last_inter.guild_id)
        await self.licenses(inter.followup, championship_config, season)

    async def pilots(self, channel: disnake.TextChannel, championship_config: dict, season: int, title=None):
        media_path = await self._generate_media(GeneratorType.PILOTS_RANKING, championship_config, season)
        await self._send_media(channel, media_path, msg=title)

    async def teams(self, channel: disnake.TextChannel, championship_config: dict, season: int, title=None):
        media_path = await self._generate_media(GeneratorType.TEAMS_RANKING, championship_config, season)
        await self._send_media(channel, media_path, msg=title)

    async def licenses(self, channel: disnake.TextChannel, championship_config: dict, season: int, title=None):
        media_path = await self._generate_media(GeneratorType.LICENSE_POINTS, championship_config, season)
        await self._send_media(channel, media_path, msg=title)

    async def _generate_media(self, generator_type:GeneratorType, championship_config: dict, season: int, metric="Total"):
        run_config = RUN_CONFIGS[generator_type]
        reader = GeneralRankingReader(
            generator_type, championship_config, season,
            f'output/{championship_config["name"]}_{generator_type.value}.png',
            metric=metric
        )
        self.renderer = Renderer(run_config)
        _logger.info('Reading from ranking sheet...')
        generator_config = reader.read()
        _logger.info('Rendering image...')
        return await asyncio.to_thread(lambda: Renderer(run_config).render(generator_config, championship_config, season))



