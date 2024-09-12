import logging
from multiprocessing import Queue
from multiprocessing.connection import Connection

from src.bot.bot import FBRT_GUILD_ID, FBRT_TWITCH_CHAN_ID, bot
from config.config import discord_bot_token
from src.bot.cogs.telemetry_cog import TelemetryCog
from src.bot.cogs.twitch_cog import TwitchCog

_logger = logging.getLogger(__name__)


def run(queue: Queue=None, connection: Connection=None, config: dict=None, skip_twitch: bool=False):
    try:
        _logger.info('Running...')
        if queue and connection and config:
            bot.add_cog(TelemetryCog(bot))
            bot.connect_telemetry(queue, connection, config)
        if not skip_twitch:
            # TWITCH
            _logger.info("Loading TWITCH cog...")
            bot.add_cog(TwitchCog(bot, FBRT_GUILD_ID, FBRT_TWITCH_CHAN_ID))
        bot.run(discord_bot_token)

    except KeyboardInterrupt:
        _logger.info('Stopping...')
    _logger.info('Stopped !')
