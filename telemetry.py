import sys
import pickle
from datetime import datetime
from threading import Thread
from disnake.ext import commands
from f1_23_telemetry.listener import TelemetryListener
import logging
from src.telemetry.brain import Brain


_logger = logging.getLogger(__name__)

class TelemetryThread(Thread):
    def __init__(self, ip:str, sheet_name:str=None, bot:commands.InteractionBot=None, championship_config:dict=None):
        super().__init__()
        self.ip = ip
        self.sheet_name = sheet_name
        self.bot = bot
        self.brain = Brain(bot, championship_config, sheet_name)

    def run(self) -> None:
        _logger.info(f'Starting listening on {self.ip}:20777')
        listener = TelemetryListener(host=self.ip)
        datetimecode = datetime.now().strftime('%Y%d%m_%H:%M:%S')
        try:
            while True:
                _logger.debug('Waiting for packets...')
                packet = listener.get()
                packet_type = type(packet)
                _logger.debug(f'{packet_type} received...')
                self.brain.handle_received_packet(packet)
        except KeyboardInterrupt:
            _logger.info('Stopping telemetry...')
            if not self.brain.current_session:
                sys.exit(130)
            session_name = f'{self.brain.current_session.session_type}_{self.brain.current_session.track}'
            with open(f"dumped_sessions/{session_name}_{datetimecode}.pickle", "wb") as out_file:
                pickle.dump(self.brain, out_file)
            sys.exit(130)
        except:
            _logger.info('Stopping telemetry because of huge fail...')
            with open(f"dumped_sessions/session_{datetimecode}.pickle", "wb") as out_file:
                pickle.dump(self.brain, out_file)
            raise
