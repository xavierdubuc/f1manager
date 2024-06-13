import asyncio
from time import sleep
from multiprocessing import Process
from config.config import CHAMPIONSHIPS

import logging
from src.time_trial_manager import TimeTrialManager
from src.bot import run as run_discord_bot, bot
from src.logging import setup as setup_logging

setup_logging('debug')

_logger = logging.getLogger(__name__)

@bot.event
async def on_ready():
    ttm = TimeTrialManager(bot)
    _logger.info('Setting up...')
    await ttm.setup()
    _logger.info('Create not existing messages...')
    # await ttm.reset()
    await ttm.update_all_circuit_messages()


CHAMPIONSHIP_CONFIG = CHAMPIONSHIPS['FBRT']

run_discord_bot()
