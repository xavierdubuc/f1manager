import sys
import pickle
from datetime import datetime
from f1_22_telemetry.packets import *
import logging
from src.telemetry.telemetry_command import Command
from pprint import pformat

from telemetry import TelemetryThread
from bot import bot
from config.config import discord_bot_token, CHAMPIONSHIPS


args = Command().parse_args()
levels = {
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}
log_level = levels[args.log_level]
print(f'Using log level : "{args.log_level}"')
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
_logger = logging.getLogger(__name__)

if args.championship not in CHAMPIONSHIPS:
    _logger.error(f'Unknown championship "{args.championship}"')
    exit()
CHAMPIONSHIP_CONFIG = CHAMPIONSHIPS[args.championship]
_logger.info(f'Will use "{args.championship}" config')
_logger.debug(f'\n{pformat(CHAMPIONSHIP_CONFIG,indent=2)}')

thread_telemetry = TelemetryThread(args.ip, args.sheet_name, bot, CHAMPIONSHIP_CONFIG)
thread_telemetry.daemon = True  # this is a problem for pickle and send to gsheet
thread_telemetry.start()

try:
    _logger.info('Starting bot...')
    bot.run(discord_bot_token)
    _logger.info('Bot stopped, hit CTRL+C again to stop telemetry')
    thread_telemetry.join()
except KeyboardInterrupt:
    _logger.info('Stopping telemetry...')
    with open(f"session{datetime.now().isoformat()}.pickle", "wb") as out_file:
        try:
            dmp = {
                'current_session': thread_telemetry.brain.current_session,
                'previous_sessions': thread_telemetry.brain.previous_sessions
            }
            pickle.dump(dmp, out_file)
        except Exception as e:
            _logger.error('Could not pickle the brain because of following exception')
            _logger.error(e)
            _logger.info('Pickling current session instead...')
            pickle.dump(thread_telemetry.brain.current_session, out_file)
    sys.exit(130)
