import sys
import pickle
from datetime import datetime
from threading import Thread
from disnake.ext import commands
from f1_22_telemetry.listener import TelemetryListener
from f1_22_telemetry.packets import *
import logging
from src.telemetry.brain import Brain
from src.gsheet.gsheet import GSheet
from config.config import DEFAULT_SPREADSHEET_ID, RACE_RANKING_RANGE

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

_logger = logging.getLogger(__name__)

class TelemetryThread(Thread):
    def __init__(self, ip:str, sheet_name:str=None, bot:commands.InteractionBot=None, discord_guild:str=None, discord_channel:str=None):
        super().__init__()
        self.ip = ip
        self.sheet_name = sheet_name
        self.bot = bot
        self.brain = Brain(bot, discord_guild, discord_channel)

    def run(self) -> None:
        _logger.info(f'Starting listening on {self.ip}:20777')
        listener = TelemetryListener(host=self.ip)
        i = 0
        datetimecode = datetime.now().strftime('%Y%d%m_%H:%M:%S')
        try:
            while True:
                _logger.debug('Waiting for packets...')
                packet = listener.get()
                packet_type = type(packet)
                _logger.debug(f'{packet_type} received...')
                self.brain.handle_received_packet(packet)
                # if self.brain.current_session and self.brain.current_session.participants:
                #     for participant in self.brain.current_session.participants:
                #         if not participant.telemetry_is_public:
                #             print(f'{participant.race_number} {participant.name} does not have public telemetry !')
                i += 1
        except KeyboardInterrupt:
            _logger.info('Stopping telemetry...')
            if not self.brain.current_session:
                sys.exit(130)
            session_name = f'{self.brain.current_session.session_type}_{self.brain.current_session.track}'
            with open(f"dumped_sessions/{session_name}_{datetimecode}.pickle", "wb") as out_file:
                pickle.dump(self.brain, out_file)
                if self.brain.current_session and self.brain.current_session.final_classification:
                    final_ranking = self.brain.current_session.get_formatted_final_ranking()
                    for row in final_ranking:
                        print('\t'.join(map(str, row)))
                    if self.sheet_name:
                        g = GSheet()
                        range_str = f"'{self.sheet_name}'!{RACE_RANKING_RANGE}"
                        g.set_sheet_values(DEFAULT_SPREADSHEET_ID, range_str, final_ranking)
                        _logger.info(f'Writing ranking above to sheet {self.sheet_name}')
            sys.exit(130)
        except:
            _logger.info('Stopping telemetry because of huge fail...')
            with open(f"dumped_sessions/session_{datetimecode}.pickle", "wb") as out_file:
                pickle.dump(self.brain, out_file)
            raise