from multiprocessing import Process, Pipe, Queue
from multiprocessing.connection import Connection
from f1_23_telemetry.listener import TelemetryListener
from config.config import discord_bot_token, CHAMPIONSHIPS
from bot import bot

import logging
from src.bot.cogs.telemetry_cog import TelemetryCog
from src.telemetry.brain import Brain
from src.telemetry.telemetry_command import Command
from pprint import pformat

from bot import bot
from config.config import discord_bot_token, CHAMPIONSHIPS

# SEND MESSAGES FROM TELEMETRY
bot.add_cog(TelemetryCog(bot))

args = Command().parse_args()
levels = {
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}
log_level = levels[args.log_level]
_logger = logging.getLogger(__name__)
_logger.info(f'Using log level : "{args.log_level}"')
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(processName)s → %(message)s",
    force=True
)

if args.championship not in CHAMPIONSHIPS:
    _logger.error(f'Unknown championship "{args.championship}"')
    exit()
CHAMPIONSHIP_CONFIG = CHAMPIONSHIPS[args.championship]
_logger.info(f'Will use "{args.championship}" config')
_logger.debug(f'\n{pformat(CHAMPIONSHIP_CONFIG,indent=2)}')


def run_discord_bot(queue: Queue, connection:Connection):
    try:
        _logger.info('Running...')
        bot.connect_telemetry(queue, connection, CHAMPIONSHIP_CONFIG)
        bot.run(discord_bot_token)

    except KeyboardInterrupt:
        _logger.info('Stopping...')
    _logger.info('Stopped !')

def run_telemetry(queue: Queue, connection:Connection):
    try:
        _logger.info('Running...')
        brain = Brain(queue, CHAMPIONSHIP_CONFIG, args.sheet_name)
        _logger.info(f'Starting listening on {args.ip}:20777')
        listener = TelemetryListener(host=args.ip)
        while True:
            _logger.debug('Waiting for packets...')
            packet = listener.get()
            packet_type = type(packet)
            _logger.debug(f'{packet_type} received...')
            brain.handle_received_packet(packet)
    except KeyboardInterrupt:
        _logger.info('Stopping...')
    _logger.info('Stopped !')


queue = Queue()
discord_conn, telemetry_conn = Pipe()
discord_process = Process(target=run_discord_bot, name=' DISCORD ', args=(queue, discord_conn))
telemetry_process = Process(target=run_telemetry, name='TELEMETRY', args=(queue, telemetry_conn))

discord_process.start()
telemetry_process.start()

discord_process.join()
telemetry_process.join()
