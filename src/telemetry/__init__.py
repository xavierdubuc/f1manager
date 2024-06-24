from multiprocessing import Queue
from multiprocessing.connection import Connection
from f1_24_telemetry.listener import TelemetryListener
from src.telemetry.brain import Brain

import logging
_logger = logging.getLogger(__name__)

def run(queue: Queue, connection: Connection, config:dict, sheet_name:str, ip:str):
    try:
        _logger.info('Running...')
        brain = Brain(queue, config, sheet_name)
        _logger.info(f'Starting listening on {ip}:20777')
        listener = TelemetryListener(host=ip)
        while True:
            _logger.debug('Waiting for packets...')
            packet = listener.get()
            packet_type = type(packet)
            _logger.debug(f'{packet_type} received...')
            brain.handle_received_packet(packet)
    except KeyboardInterrupt:
        _logger.info('Stopping...')
    _logger.info('Stopped !')
