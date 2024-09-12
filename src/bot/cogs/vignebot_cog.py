import logging
from typing import Dict, Tuple

import disnake
from disnake.ext import commands
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.bot.vignebot import Vignebot
from config.config import DISCORDS


_logger = logging.getLogger(__name__)


class VignebotCog(commands.Cog):
    last_inter: disnake.ApplicationCommandInteraction = None

    def __init__(self, bot: Vignebot):
        self.bot = bot
        self.last_inter = None

    async def _bootstrap(self, inter: disnake.ApplicationCommandInteraction, **kwargs):
        str_params = ', '.join(f"{k}={v}" for k, v in kwargs.items())
        _logger.info(f'{inter.user.display_name} called {self.__cog_name__}({str_params})')
        await inter.response.defer()
        self.last_inter = inter

    def _get_discord_config(self, discord_id: int) -> Tuple[Dict, str]:
        championship_config = DISCORDS[discord_id]
        _logger.info(f'Will use google sheet of {championship_config["name"]}')
        season = championship_config['current_season']
        return championship_config, season

    async def _send_media(self, channel: disnake.TextChannel, media_path: str, msg: str = None):
        if not media_path:
            await channel.send('Le visuel était vide, êtes-vous sûr que le Sheet est bien rempli ?')
            return
        _logger.info('Sending media...')
        with open(media_path, 'rb') as f:
            picture = disnake.File(f)
            if msg:
                await channel.send(content=msg, file=picture)
            else:
                await channel.send(file=picture)
            _logger.info('Media sent !')

    def _get_channel(self, discord_config:dict, feed:str) -> disnake.TextChannel:
        config = discord_config[feed]
        guild = self.bot.get_guild(config['guild'])
        return guild.get_channel(config['chann'])

    async def _fetch_channel(self, discord_config:dict, feed:str):
        config = discord_config[feed]
        guild = await self.bot.fetch_guild(config['guild'])
        return await guild.fetch_channel(config['chann'])
