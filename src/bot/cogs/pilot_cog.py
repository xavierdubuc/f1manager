import logging
import disnake
from disnake.ext import commands
from src.media_generation.generators.pilot_generator import PublicException
from src.media_generation.helpers.reader import Reader
from src.bot.cogs.vignebot_cog import VignebotCog
from src.media_generation.data import teams_idx
from src.media_generation.helpers.renderer import Renderer
from src.media_generation.helpers.generator_type import GeneratorType
from src.bot.vignebot import Vignebot
from src.media_generation.run_config import RUN_CONFIGS


_logger = logging.getLogger(__name__)

TEAMS = list(teams_idx.keys())

WHO_PARAM = commands.Param(
    name="nom",
    description="Le nom du pilote"
)
VISUAL_TYPE_PARAM = commands.Param(
    name="type_visuel",
    choices=["lineup", 'closeup', 'whole'],
    description="Type de visuel",
    default='lineup'
)
TEAM_PARAM = commands.Param(
    name='equipe',
    default=None,
    choices=TEAMS,
    description="L'équipe (celle de la saison actuelle par défaut)"
)


class PilotCog(VignebotCog):

    def __init__(self, bot: Vignebot):
        super().__init__(bot)
        self.run_config = RUN_CONFIGS[GeneratorType.PILOT]
        self.renderer = Renderer(self.run_config)

    @commands.slash_command(name="pilot", description='Pilot')
    async def run(self, inter: disnake.ApplicationCommandInteraction,
                  who: str = WHO_PARAM,
                  visual_type: str = VISUAL_TYPE_PARAM,
                  team: str = TEAM_PARAM,):
        await self._bootstrap(inter, who=who, visual_type=visual_type, team=team)
        championship_config, season = self._get_discord_config(inter.guild_id)
        _logger.info('Reading sheet...')
        config = Reader(GeneratorType.PILOT, championship_config,
                        season, f'output/pilot_{who}.png').read()
        _logger.info('Rendering image...')
        try:
            output_filepath = self.renderer.render(
                config, championship_config, season, who,
                team=team, visual_type=visual_type
            )
            await self._send_media(inter.followup, output_filepath)
            _logger.info('Image sent !')
        except PublicException as e:
            await inter.followup.send(str(e))
