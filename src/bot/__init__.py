import logging
from multiprocessing import Queue
from multiprocessing.connection import Connection

from src.bot.bot import bot
from config.config import discord_bot_token
from src.bot.cogs.telemetry_cog import TelemetryCog

_logger = logging.getLogger(__name__)


def run(queue: Queue=None, connection: Connection=None, config: dict=None):
    try:
        _logger.info('Running...')
        if queue and connection and config:
            bot.add_cog(TelemetryCog(bot))
            bot.connect_telemetry(queue, connection, config)
        bot.run(discord_bot_token)

    except KeyboardInterrupt:
        _logger.info('Stopping...')
    _logger.info('Stopped !')
