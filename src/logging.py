import logging

LEVELS = {
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

def setup(log_level_str:str=None):
    log_level = LEVELS.get(log_level_str, 'INFO')
    _logger = logging.getLogger(__name__)
    _logger.info(f'Using log level : "{log_level_str}"')
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(processName)s → %(message)s",
        force=True
    )
