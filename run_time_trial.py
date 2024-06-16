import argparse
from config.config import CHAMPIONSHIPS

import logging
from src.time_trial.time_trial_manager import TimeTrialManager
from src.bot import run as run_discord_bot, bot
from src.logging import setup as setup_logging

setup_logging('debug')

_logger = logging.getLogger(__name__)


class Command(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument("command", help="Command to execute (fetch/reset/update)")
        self.add_argument("-i", '--ip', help="Ip address", default='192.168.1.15')
        self.add_argument("-c", "--championship", help="Championship concerned", dest='championship', default='FBRT')
        self.add_argument("-a", "--season", help="Season (only used in standings)",
                          dest='season', default=None, type=int)
        self.add_argument("-n", "--circuit", help="Circuit name", dest='circuit_name', default=None)


args = Command().parse_args()
_logger.info('Parameters:')
_logger.info(f'\t command: {args.command}')
_logger.info(f'\t championship: {args.championship}')
_logger.info(f'\t season: {args.season}')
_logger.info(f'\t circuit: {args.circuit_name}')

CHAMPIONSHIP_CONFIG = CHAMPIONSHIPS[args.championship]

ttm = TimeTrialManager(bot)

if args.command == 'fetch':
    ttm.fetch_from_game(args.ip)
else:
    @bot.event
    async def on_ready():
        _logger.info('Setting up...')
        await ttm.setup()
        _logger.info('Create not existing messages...')
        if args.command == 'reset':
            await ttm.reset()
        elif args.command == 'update_all':
            await ttm.update_all_circuit_messages()

    run_discord_bot()
