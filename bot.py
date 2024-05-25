import logging
from typing import Dict, Tuple
import disnake
from disnake.ext import commands
from src.bot.cogs.twitch_cog import TwitchCog
from src.media_generation.generators.pilot_generator import PublicException
from src.bot.vignebot import Vignebot
import src.bot.presence_embed as PresenceEmbed
import src.bot.breaking_command as BreakingCommand
import src.bot.quote_command as QuoteCommand
import src.bot.after_race_command as AfterRaceCommand
import src.bot.confirm_results_command as ConfirmResultsCommand
import src.bot.race_command as RaceCommand
import src.bot.pilot_command as PilotCommand
import src.bot.rankings_command as RankingCommand

from src.media_generation.data import teams_idx
from config import DISCORDS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

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

############
# EVENT LISTENERS
############


@bot.event
async def on_ready():
    _logger.info('Connected !')


@bot.listen("on_button_click")
async def button_listener(inter: disnake.MessageInteraction):
    await PresenceEmbed.button_clicked(inter)


@bot.event
async def on_message(msg: disnake.Message):
    if bot.user.mentioned_in(msg) and not msg.mention_everyone and msg.type != disnake.MessageType.reply:
        # TODO calepino
        await msg.channel.send("Vous m'avez appelé ? Ne vous en faites Gaëtano est là ! J'vous ai déjà parlé de mon taximan brésilien ?")


############
# SLASH COMMANDS
############


# ##### /rankings


@bot.slash_command(name="rankings", description='Rankings')
async def rankings(
    inter: disnake.ApplicationCommandInteraction,
    what: str = RankingCommand.WHAT_PARAM,
    metric: str = RankingCommand.METRIC_PARAM
):
    _logger.info(f'{inter.user.display_name} called Rankings(what={what}, metric={metric})')
    await inter.response.defer()
    championship_config, season = _get_discord_config(inter.guild_id)
    await RankingCommand.run(inter, what, metric, championship_config, season)


# ##### /race


@bot.slash_command(name="race", description='Race information')
async def race(
    inter: disnake.ApplicationCommandInteraction,
    race_number: str = RaceCommand.RACE_NUMBER_PARAM,
    what: str = RaceCommand.WHAT_PARAM
):
    _logger.info(f'{inter.user.display_name} called Race(race_number={race_number}, what={what})')
    await inter.response.defer()
    championship_config, season = _get_discord_config(inter.guild_id)
    await RaceCommand.run(inter, race_number, what, championship_config, season)


# ##### /confirmresults


@bot.slash_command(name="confirmresults", description="Confirm results")
async def confirmresults(
    inter: disnake.ApplicationCommandInteraction,
    runtype: str = ConfirmResultsCommand.RUNTYPE_PARAM,
    race_number: str = RaceCommand.RACE_NUMBER_PARAM
):
    _logger.info(f'{inter.user.display_name} called ConfirmResults(race_number={race_number})')
    await inter.response.defer()
    championship_config, season = _get_discord_config(inter.guild_id)
    await ConfirmResultsCommand.run(inter, runtype, race_number, championship_config, season)


# ##### /afterrace


@bot.slash_command(name="afterrace", description='Do all what has to be done after race')
async def afterrace(
    inter: disnake.ApplicationCommandInteraction,
    runtype: str = AfterRaceCommand.RUNTYPE_PARAM,
    race_number: str = RaceCommand.RACE_NUMBER_PARAM
):
    _logger.info(f'{inter.user.display_name} called AfterRace(race_number={race_number})')
    await inter.response.defer()
    championship_config, season = _get_discord_config(inter.guild_id)
    await AfterRaceCommand.run(inter, runtype, race_number, championship_config, season)


# ##### /breaking


@bot.slash_command(name="breaking", description='Breaking !')
async def breaking(
    inter: disnake.ApplicationCommandInteraction,
    img: disnake.Attachment = BreakingCommand.IMG_PARAM,
    main_txt: str = BreakingCommand.MAIN_TXT_PARAM,
    secondary_txt: str = BreakingCommand.SECONDARY_TXT_PARAM,
    team: str = BreakingCommand.TEAM_PARAM,
    background: str = BreakingCommand.BG_PARAM,
    foreground: str = BreakingCommand.FG_PARAM,
    padding_top: int = BreakingCommand.PADDING_TOP_PARAM
):
    _logger.info(f'{inter.user.display_name} called Breaking(main_txt={main_txt}, secondary_txt={secondary_txt}, team={team}, bg={background}, fg={foreground}, pt={padding_top})')
    await inter.response.defer()
    await BreakingCommand.run(inter, img, main_txt, secondary_txt, team, background, foreground, padding_top)


# ##### /quote


@bot.slash_command(name="quote", description='Citation')
async def quote(
    inter: disnake.ApplicationCommandInteraction,
    img: disnake.Attachment = QuoteCommand.IMG_PARAM,
    author: str = QuoteCommand.AUTHOR_PARAM,
    quote: str = QuoteCommand.QUOTE_PARAM,
    team: str = QuoteCommand.TEAM_PARAM,
    background: str = QuoteCommand.BG_PARAM,
    foreground: str = QuoteCommand.FG_PARAM,
    padding_top: int = QuoteCommand.PADDING_TOP_PARAM
):
    _logger.info(f'{inter.user.display_name} called Quote(author={author}, quote={quote}, team={team}, bg={background}, fg={foreground}, pt={padding_top})')
    await inter.response.defer()
    await QuoteCommand.run(inter, img, author, quote, team, background, foreground, padding_top)


# ##### /pilot


@bot.slash_command(name="pilot", description='Pilot')
async def pilot(
    inter: disnake.ApplicationCommandInteraction,
    who: str = PilotCommand.WHO_PARAM,
    visual_type: str = PilotCommand.VISUAL_TYPE_PARAM,
    team: str = PilotCommand.TEAM_PARAM,
):
    _logger.info(f'{inter.user.display_name} called Pilot(who={who}, visual_type={visual_type}, team={team})')
    await inter.response.defer()
    championship_config, season = _get_discord_config(inter.guild_id)
    try:
        await PilotCommand.run(inter, who, visual_type, team, championship_config, season)
    except PublicException as e:
        await inter.followup.send(str(e))


############
# HELPERS
############


def _get_discord_config(discord_id: int) -> Tuple[Dict, str]:
    championship_config = DISCORDS[discord_id]
    _logger.info(f'Reading google sheet for {championship_config["name"]}')
    season = DISCORDS[discord_id]['current_season']
    return championship_config, season


############
# ERROR HANDLING
############


original_error_handler = bot.on_slash_command_error


async def on_slash_command_error(inter: disnake.ApplicationCommandInteraction, exception):
    await inter.delete_original_message()
    await inter.channel.send(f"Une erreur est survenue dans la génération, contactez Xion.\nL'exception générée est : {str(exception)}")
    _logger.exception(exception)
    await original_error_handler(inter, exception)

bot.on_slash_command_error = on_slash_command_error
