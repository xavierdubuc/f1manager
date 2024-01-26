import logging
import disnake
from disnake.ext import commands
from src.bot import presence_embed as PresenceEmbed

import src.bot.race_vote_driveroftheday as VoteDriverOfTheDay
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.helpers.generator_type import GeneratorType
from src.media_generation.helpers.renderer import Renderer
from src.media_generation.readers.race_reader import RaceReader
from src.media_generation.run_config import RUN_CONFIGS
_logger = logging.getLogger(__name__)

RACE_NUMBER_PARAM = commands.Param(
    name="race_number",
    description='Le numéro de la course'
)
WHAT_PARAM = commands.Param(
    name="what",
    choices=[
        'presences', 'presentation', 'lineups', 'grid_ribbon', 'grid', 'results',
        'vote_driveroftheday', 'driver_of_the_day'
    ]
)


def read_config(race_number: str, visual:str, generator_type:GeneratorType, championship_config:dict, season:int) -> GeneratorConfig:
    sheet_name = f'Race {race_number}'
    return RaceReader(generator_type, championship_config,
                        season, f'output/race_{visual}.png', sheet_name).read()

async def run(inter: disnake.ApplicationCommandInteraction, race_number: str, what: str, championship_config: dict, season: int, channel: disnake.TextChannel = None, config: GeneratorConfig = None):
    if what == 'presences':
        visual = 'presentation'
    elif what == 'vote_driveroftheday':
        visual = 'results'
    else:
        visual = what

    generator_type = GeneratorType(visual)
    run_config = RUN_CONFIGS[generator_type]
    config = config or read_config(race_number, visual, generator_type, championship_config, season)

    if what == 'presences':
        await PresenceEmbed.send_initial_messages(inter, config.race, channel)
        return

    if what == 'vote_driveroftheday':
        await VoteDriverOfTheDay.send_initial_message(inter, config.race, channel)
        return

    _logger.info('Rendering image...')
    output_filepath = Renderer(run_config).render(
        config, championship_config, season)
    if not output_filepath:
        await (channel or inter.followup).send('Le visuel était vide, êtes-vous sûr que le Sheet est bien rempli ?')
        return

    _logger.info('Sending image...')
    with open(output_filepath, 'rb') as f:
        picture = disnake.File(f)
        await (channel or inter.followup).send(file=picture)
        _logger.info('Image sent !')
