from src.media_generation.helpers.reader import Reader
from src.media_generation.helpers.calendar_reader import CalendarReader
from src.media_generation.helpers.general_ranking_reader import GeneralRankingReader
from src.media_generation.helpers.renderer import Renderer
from src.media_generation.helpers.command import Command
from src.media_generation.helpers.generator_config import GeneratorType
from pprint import pformat
from config.config import CHAMPIONSHIPS
import os.path

import logging

GENERAL_RANKING_TYPES = (GeneratorType.TeamsRanking.value, GeneratorType.PilotsRanking.value)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
_logger = logging.getLogger(__name__)

args = Command().parse_args()
_logger.info('Parameters:')
_logger.info(f'\t championship: {args.championship}')
_logger.info(f'\t season: {args.season}')
_logger.info(f'\t output: {args.output}')
_logger.info(f'\t sheet: {args.sheet}')
_logger.info(f'\t metric: {args.metric}')

if args.championship not in CHAMPIONSHIPS:
    _logger.error(f'Unknown championship "{args.championship}"')
    exit()
CHAMPIONSHIP_CONFIG = CHAMPIONSHIPS[args.championship]
_logger.info(f'Will use "{args.championship}" config')
_logger.debug(f'\n{pformat(CHAMPIONSHIP_CONFIG,indent=2)}')

if args.season is None:
    season = sorted(CHAMPIONSHIP_CONFIG['seasons'].keys())[-1]
else:
    season = args.season
_logger.info(f'Season {season} selected')

READER_CLASS = Reader
if args.type in GENERAL_RANKING_TYPES:
    READER_CLASS = GeneralRankingReader
elif args.type == 'calendar':
    READER_CLASS = CalendarReader

_logger.info(f'Will use "{READER_CLASS.__name__}" to read sheet data')

reader = READER_CLASS(
    args.type, CHAMPIONSHIP_CONFIG, season,
    args.output, args.sheet, args.metric
)
championship_data = reader.read()
_logger.info('Rendering...')
output_filepath = Renderer.render(championship_data, CHAMPIONSHIP_CONFIG, season)
_logger.info(f'Image successfully rendered in file "{os.path.realpath(output_filepath)}"')
