from threading import Thread
from f1_22_telemetry.packets import *
import logging
from src.telemetry.telemetry_command import Command

from telemetry import run_telemetry
# from bot import bot

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

run_telemetry(args.ip, args.sheet_name, None)
# thread_telemetry = Thread(target=lambda: run_telemetry(args.ip, bot))
# thread_telemetry.daemon = True
# thread_telemetry.start()

# _logger.info('Starting bot...')
# bot.run(token)
