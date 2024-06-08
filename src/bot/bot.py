import logging
import disnake
from disnake.ext import commands
from src.bot.cogs.pilot_cog import PilotCog
from src.bot.cogs.confirm_results_cog import ConfirmResultsCog
from src.bot.cogs.after_race_cog import AfterRaceCog
from src.bot.cogs.ranking_cog import RankingCog
from src.bot.cogs.presences_cog import PresencesCog
from src.bot.cogs.driver_of_the_day_cog import DriverOfTheDayCog
from src.bot.cogs.grid_cog import GridCog
from src.bot.cogs.lineup_cog import LineupCog
from src.bot.cogs.presentation_cog import PresentationCog
from src.bot.cogs.results_cog import ResultsCog
from src.bot.cogs.twitch_cog import TwitchCog
from src.media_generation.generators.pilot_generator import PublicException
from src.bot.vignebot import Vignebot

from src.media_generation.data import teams_idx
from config import DISCORDS

_logger = logging.getLogger(__name__)
TEAMS = list(teams_idx.keys())

command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True

intents = disnake.Intents.default()
intents.members = True
bot = Vignebot(command_sync_flags=command_sync_flags, intents=intents)

FBRT_GUILD_ID = 923505034778509342
FBRT_BOT_CHAN_ID = 1074632856443289610
FBRT_TWITCH_CHAN_ID = 925683581026729984
DEBUG_GUILD_ID = 1074380392154533958
DEBUG_CHAN_ID = 1096169137589461082

FBRT_TWITCH_USER_ID = '756827903'
SEPHELDOR_TWITCH_USER_ID = '72670233'
WATCHED_TWITCH_IDS = [FBRT_TWITCH_USER_ID]
IS_LIVE = {}

############
# COGS
############

# TWITCH
bot.add_cog(TwitchCog(bot, FBRT_GUILD_ID, FBRT_TWITCH_CHAN_ID))

# PRESENCES
bot.add_cog(PresencesCog(bot))

# PRESENTATION
bot.add_cog(PresentationCog(bot))

# LINEUP
bot.add_cog(LineupCog(bot))

# GRID
bot.add_cog(GridCog(bot))

# RESULTS
bot.add_cog(ResultsCog(bot))

# DRIVER OF THE DAY
bot.add_cog(DriverOfTheDayCog(bot))

# RANKINGS
bot.add_cog(RankingCog(bot))

# AFTER RACE
bot.add_cog(AfterRaceCog(bot))

# CONFIRM RESULTS
bot.add_cog(ConfirmResultsCog(bot))

# BREAKING TODO
# bot.add_cog(BreakingCog(bot))

# QUOTE TODO
# bot.add_cog(QuoteCog(bot))

# PILOT
bot.add_cog(PilotCog(bot))

# SEASON RAKING TODO
# bot.add_cog(SeasonRankingCog(bot))

# TODO idée lisant le calendrier "@vignebot où est la prochaine course ?"
# TODO un excel où un circuit = une page et chaque page contient le classement CLM
# chaque page contient aussi l'identifiant du message discord correspondant
# -> script pour créer ces liens + le message de sommaire
# -> script pour mettre à jour l'excel sur base des données du jeu directement
# -> script pour demander au bot de mettre à jour un post sur base de l'excel

############
# EVENT LISTENERS
############


@bot.event
async def on_ready():
    _logger.info('Connected !')


@bot.event
async def on_message(msg: disnake.Message):
    if bot.user.mentioned_in(msg) and not msg.mention_everyone and msg.type != disnake.MessageType.reply:
        # TODO calepino
        await msg.channel.send("Vous m'avez appelé ? Ne vous en faites Gaëtano est là ! J'vous ai déjà parlé de mon taximan brésilien ?")


############
# ERROR HANDLING
############


original_error_handler = bot.on_slash_command_error


async def on_slash_command_error(inter: disnake.ApplicationCommandInteraction, exception):
    # await inter.delete_original_message()
    await inter.channel.send(f"Une erreur est survenue dans la génération, contactez Xion.\nL'exception générée est : {str(exception)}")
    _logger.exception(exception)
    await original_error_handler(inter, exception)

bot.on_slash_command_error = on_slash_command_error
