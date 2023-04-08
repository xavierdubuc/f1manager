from src.media_generation.helpers.reader import Reader
from src.media_generation.helpers.calendar_reader import CalendarReader
from src.media_generation.helpers.general_ranking_reader import GeneralRankingReader
from src.media_generation.helpers.renderer import Renderer
from src.media_generation.helpers.command import Command
from src.media_generation.helpers.generator_config import GeneratorType
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
if args.type in GENERAL_RANKING_TYPES:
    config = GeneralRankingReader(args.type, args.input, args.output, args.season, args.metric).read()
elif args.type == 'calendar':
    config = CalendarReader(args.type, args.input, args.output, args.season).read()
else:
    config = Reader(args.type, args.input, args.sheet, args.output).read()
output_filepath = Renderer.render(config)
_logger.info(f'Image successfully rendered in file "{os.path.realpath(output_filepath)}"')
