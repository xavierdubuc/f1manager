import logging
import disnake
from disnake.ext import commands
from src.media_generation.data import teams_idx
from src.media_generation.helpers.generator_type import GeneratorType
from src.media_generation.helpers.reader import Reader
from src.media_generation.helpers.renderer import Renderer
from src.media_generation.run_config import RUN_CONFIGS

_logger = logging.getLogger(__name__)

TEAMS = list(teams_idx.keys())

WHO_PARAM = commands.Param(
    name="name",
    description="Le nom du pilote"
)
VISUAL_TYPE_PARAM = commands.Param(
    name="visual_type",
    choices=["lineup", 'closeup', 'whole'],
    description="Type de visuel",
    default='lineup'
)
TEAM_PARAM = commands.Param(
    name='team',
    default=None,
    choices=TEAMS,
    description="L'équipe (celle de la saison actuelle par défaut)"
)


async def run(
    inter: disnake.ApplicationCommandInteraction,
    who: str,
    visual_type: str,
    team: str,
    championship_config:dict,
    season:int
):
    run_config = RUN_CONFIGS[GeneratorType.PILOT]
    config = Reader(
        GeneratorType.PILOT, championship_config,
                    season, f'output/pilot_{who}.png').read()
    _logger.info('Rendering image...')
    output_filepath = Renderer(run_config).render(
        config, championship_config, season, who, team=team, visual_type=visual_type
    )
    _logger.info('Sending image...')
    with open(output_filepath, 'rb') as f:
        picture = disnake.File(f)
        await inter.followup.send(file=picture)
        _logger.info('Image sent !')
