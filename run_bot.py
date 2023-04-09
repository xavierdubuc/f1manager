import logging
from bot import bot
from config.config import discord_bot_token

levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}
print(f'Using log level : INFO')
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
_logger = logging.getLogger(__name__)

_logger.info('Starting bot...')
bot.run(discord_bot_token)
