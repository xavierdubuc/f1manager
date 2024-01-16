import logging
import disnake

from disnake.ext import commands
from src.media_generation.helpers.generator_type import GeneratorType
from src.media_generation.helpers.renderer import Renderer
from src.media_generation.readers.general_ranking_reader import GeneralRankingReader
from src.media_generation.run_config import RUN_CONFIGS

_logger = logging.getLogger(__name__)


WHAT_PARAM = commands.Param(
    name="what",
    choices=["teams", "pilots", 'license_points'],
    description="Le classement désiré"
)

METRIC_PARAM = commands.Param(
    name="metric",
    choices=['Points', 'Points par course'],
    description="La métrique à utiliser pour les points et pour trier le classement",
    default='Points'
)


async def run(inter: disnake.ApplicationCommandInteraction, what: str, metric: str, championship_config: dict, season: int, channel: disnake.TextChannel = None):
    tech_metric = 'Total' if metric == 'Points' else metric
    generator_type = GeneratorType(
        f'{what}_ranking' if what in ('teams', 'pilots') else what)
    run_config = RUN_CONFIGS[generator_type]
    config = GeneralRankingReader(
        generator_type,
        championship_config,
        season,
        f'{championship_config["name"]}rankings.png',
        metric=tech_metric).read()
    _logger.info('Rendering image...')
    output_filepath = Renderer(run_config).render(
        config, championship_config, season)
    _logger.info('Sending image...')
    with open(output_filepath, 'rb') as f:
        picture = disnake.File(f)
        await (channel or inter.followup).send(file=picture)
        _logger.info('Image sent !')
