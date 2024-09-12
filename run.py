from multiprocessing import Process, Pipe, Queue
from config.config import CHAMPIONSHIPS

import logging
from src.bot import run as run_discord_bot
from src.telemetry import run as run_telemetry
from src.logging import setup as setup_logging
from src.telemetry.telemetry_command import Command
from pprint import pformat

args = Command().parse_args()
setup_logging(args.log_level)

_logger = logging.getLogger(__name__)

if args.championship not in CHAMPIONSHIPS:
    _logger.error(f'Unknown championship "{args.championship}"')
    exit()
CHAMPIONSHIP_CONFIG = CHAMPIONSHIPS[args.championship]
_logger.info(f'Will use "{args.championship}" config')
_logger.debug(f'\n{pformat(CHAMPIONSHIP_CONFIG,indent=2)}')


queue = Queue()
discord_conn, telemetry_conn = Pipe()
discord_process = Process(
    target=run_discord_bot, name=' DISCORD ',
    args=(queue, discord_conn, CHAMPIONSHIP_CONFIG, args.skip_twitch)
)
telemetry_process = Process(
    target=run_telemetry, name='TELEMETRY',
    args=(queue, telemetry_conn, CHAMPIONSHIP_CONFIG, args.sheet_name, args.ip)
)

discord_process.start()
telemetry_process.start()

discord_process.join()
telemetry_process.join()
