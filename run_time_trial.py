import argparse
from config.config import CHAMPIONSHIPS

import logging
from src.time_trial.time_trial_manager import TimeTrialManager
from src.bot import run as run_discord_bot, bot
from src.logging import setup as setup_logging
from src.media_generation.data import circuits as CIRCUITS

setup_logging('info')

_logger = logging.getLogger(__name__)


class Command(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument("command", help="Command to execute (fetch/reset/update)")
        self.add_argument("-i", '--ip', help="Ip address", default='192.168.1.59')
        self.add_argument("-c", "--championship", help="Championship concerned", dest='championship', default='FBRT')
        self.add_argument("-t", "--circuit", help="Circuit name", dest='circuit_name', default=None)


args = Command().parse_args()
_logger.info('Parameters:')
_logger.info(f'\t command: {args.command}')
_logger.info(f'\t championship: {args.championship}')
_logger.info(f'\t circuit: {args.circuit_name}')

CHAMPIONSHIP_CONFIG = CHAMPIONSHIPS[args.championship]

ttm = TimeTrialManager(bot)

@bot.event
async def on_ready():
    _logger.info('Setting up...')
    await ttm.setup()
    if args.command == 'reset':
        _logger.info(f'Resetting all time trial information in sheet and on Discord')
        await ttm.reset()
    elif args.command == 'update_all':
        _logger.info(f'Updating all time trial information on Discord')
        await ttm.update_all_circuit_messages()
    elif args.command == 'update':
        circuit = CIRCUITS.get(args.circuit_name)
        _logger.info(f'Updating "{circuit.name}" time trial information on Discord')
        await ttm.update_circuit_message(circuit)
    await bot.close()

if args.command == 'fetch':
    ttm.fetch_from_game(args.ip)
else:
    run_discord_bot()
