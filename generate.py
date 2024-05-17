from src.media_generation.generators.exceptions import IncorrectDataException
from src.media_generation.helpers.renderer import Renderer
from src.media_generation.helpers.command import Command
from src.media_generation.helpers.generator_type import GeneratorType
from pprint import pformat
from config.config import CHAMPIONSHIPS
import os.path

import logging

from src.media_generation.run_config import RUN_CONFIGS, RunConfig

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
_logger.info(f'\t identifier: {args.identifier}')

# VALIDATE CHAMPIONSHIP
if args.championship not in CHAMPIONSHIPS:
    _logger.error(f'Unknown championship "{args.championship}", use one of {list(CHAMPIONSHIPS.keys())}')
    exit()
CHAMPIONSHIP_CONFIG = CHAMPIONSHIPS[args.championship]
_logger.info(f'Will use "{args.championship}" config')
_logger.debug(f'\n{pformat(CHAMPIONSHIP_CONFIG,indent=2)}')

# VALIDATE SEASON
if args.season is None:
    season = sorted(CHAMPIONSHIP_CONFIG['seasons'].keys())[-1]
else:
    season = args.season
_logger.info(f'Season {season} selected')

# VALIDATE TYPE
try:
    visual_type = GeneratorType(args.type)
except ValueError:
    _logger.error(f'Unknown generator type "{args.type}", supported ones are below.')
    _logger.error([g.value for g in GeneratorType])
    exit()

run_config:RunConfig = RUN_CONFIGS[visual_type]
READER_CLASS = run_config.Reader
_logger.info(f'Will use "{READER_CLASS.__name__}" to read sheet data')

reader = READER_CLASS(
    visual_type, CHAMPIONSHIP_CONFIG, season,
    args.output, args.sheet, metric=args.metric
)
championship_data = reader.read()
_logger.info('Rendering...')
renderer = Renderer(run_config)
try:
    output_filepath = renderer.render(championship_data, CHAMPIONSHIP_CONFIG, season, args.identifier or None)
    _logger.info(f'Image successfully rendered in file "{os.path.realpath(output_filepath)}"')
except IncorrectDataException as e:
    _logger.error(f'An error occured during generation : {str(e)}')
