import logging
from time import sleep
from typing import Dict, Tuple
import disnake
from disnake.ext import commands, tasks
from twitchAPI.twitch import Twitch
from datetime import datetime
from src.media_generation.generators.pilot_generator import PublicException
import src.presence_embed as PresenceEmbed
from src.media_generation.helpers.reader import Reader
from src.media_generation.helpers.general_ranking_reader import GeneralRankingReader
from src.media_generation.helpers.renderer import Renderer

from breaking import Renderer as BreakingRenderer
from quote import Renderer as QuoteRenderer

from src.media_generation.data import teams_idx
from config import DISCORDS
from config import twitch_app_id, twitch_app_secret

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

_logger = logging.getLogger(__name__)
TEAMS = list(teams_idx.keys())

PRESENT_EMOJI = '✅'
AWAY_EMOJI = '❌'
VOTE_EMOJI = '❤️'
VOTES_EMOJIS = '🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵🇶🇷🇸🇹'
CIRCUIT_EMOJIS = {
    'Portimao': '🇵🇹',
    'Singapour': '🇸🇬',
    'Spielberg': '🇦🇹',
    'Melbourne': '🇦🇺',
    'Zandvoort': '🇳🇱',
    'Las Vegas': '🇺🇸',
    'Miami': '🇺🇸',
    'Shanghai': '🇨🇳',
    'Budapest': '🇭🇺',
    'Monza': '🇮🇹',
    'Barcelona': '🇪🇸',
    'Montréal': '🇨🇦',
}
PRESENCE_EMOJIS = [PRESENT_EMOJI, AWAY_EMOJI]

command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True

intents = disnake.Intents.default()
intents.members = True
bot = commands.InteractionBot(command_sync_flags=command_sync_flags, intents=intents)

FBRT_GUILD_ID = 923505034778509342
FBRT_BOT_CHAN_ID = 1074632856443289610
FBRT_TWITCH_CHAN_ID = 925683581026729984
DEBUG_GUILD_ID = 1074380392154533958
DEBUG_CHAN_ID = 1096169137589461082

FBRT_TWITCH_USER_ID = '756827903'
SEPHELDOR_TWITCH_USER_ID = '72670233'
WATCHED_TWITCH_IDS = [FBRT_TWITCH_USER_ID]
IS_LIVE = {}

async def _check_twitch_status(bot:commands.InteractionBot, guild_id:int, channel_id:int):
    twitch = await Twitch(twitch_app_id, twitch_app_secret)
    _logger.info('Executing Twitch status check...')
    treated = {}
    async for stream in twitch.get_streams(user_id=WATCHED_TWITCH_IDS):
        _logger.info(f'{stream.user_name} is live !')
        treated[stream.user_id] = stream.user_name
        if stream.user_id not in IS_LIVE:
            IS_LIVE[stream.user_id] = stream.user_name
            ctx = bot.get_guild(guild_id).get_channel(channel_id)
            msg = f'{stream.user_name} est en live, viens nous rejoindre sur https://twitch.tv/{stream.user_name.lower()} !'
            await ctx.send(msg)
        else:
            _logger.info('... but already notified, just ignore it')

    _logger.info('Checking not treated watched twitch ids state...')
    for id in WATCHED_TWITCH_IDS:
        if id not in treated and id in IS_LIVE:
            live_name = IS_LIVE[id]
            _logger.info(f'{live_name} is no more live !')
            del IS_LIVE[id]
            ctx = bot.get_guild(guild_id).get_channel(channel_id)
            msg = f'Le live de {live_name} est terminé, tu peux voir le replay sur https://twitch.tv/{live_name.lower()} !'
            await ctx.send(msg)
    _logger.info('Done.')

@tasks.loop(seconds=120)
async def twitch_status_checker():
    # await _check_twitch_status(bot, DEBUG_GUILD_ID, DEBUG_CHAN_ID)
    await _check_twitch_status(bot, FBRT_GUILD_ID, FBRT_TWITCH_CHAN_ID)

@bot.event
async def on_ready():
    if not twitch_status_checker.is_running():
        twitch_status_checker.start()
    msg = f'Mesdames messieurs {"bonjour" if 5 < datetime.now().hour < 17 else "bonsoir"} !'
    # await bot.get_guild(DEBUG_GUILD_ID).get_channel(DEBUG_CHAN_ID).send(msg, tts=True)
    _logger.info('Connected !')

@bot.listen("on_button_click")
async def button_listener(inter: disnake.MessageInteraction):
    await PresenceEmbed.button_clicked(inter)

@bot.event
async def on_message(msg: disnake.Message):
    if bot.user.mentioned_in(msg) and not msg.mention_everyone and msg.type != disnake.MessageType.reply:
        # TODO calepino
        await msg.channel.send("Vous m'avez appelé ? Ne vous en faites Gaëtano est là ! J'vous ai déjà parlé de mon taximan brésilien ?")


@bot.slash_command(name="rankings", description='Rankings')
async def rankings(inter,
                   what: str = commands.Param(
                       name="what",
                       choices=["teams", "pilots"],
                       description="Teams pour le classement des équipes, pilots pour les pilotes"
                   ),
                   metric: str = commands.Param(
                       name="metric",
                       choices=['Points', 'Points par course'],
                       description="La métrique à utiliser pour les points et pour trier le classement",
                       default='Points'
                   )
                   ):
    _logger.info(f'{inter.user.display_name} called Rankings(what={what}, metric={metric})')

    await inter.response.defer()

    championship_config, season = _get_discord_config(inter.guild_id)
    tech_metric = 'Total' if metric == 'Points' else metric
    config = GeneralRankingReader(
        f'{what}_ranking',
        championship_config,
        season,
        f'{championship_config["name"]}rankings.png',
        metric=tech_metric).read()
    _logger.info('Rendering image...')
    output_filepath = Renderer.render(config, championship_config, season)
    _logger.info('Sending image...')
    with open(output_filepath, 'rb') as f:
        picture = disnake.File(f)
        await inter.followup.send(file=picture)
        _logger.info('Image sent !')


@bot.slash_command(name="race", description='Race information')
async def race(inter: disnake.ApplicationCommandInteraction,
               race_number: str = commands.Param(name="race_number", description='Le numéro de la course'),
               what: str = commands.Param(
                   name="what",
                   choices=[
                       'presences', 'presentation', 'lineup', 'grid_ribbon', 'results',
                       'vote_driveroftheday', 'driver_of_the_day'
                   ])
               ):
    _logger.info(f'{inter.user.display_name} called Race(race_number={race_number}, what={what})')
    sheet_name = f'Race {race_number}'
    await inter.response.defer()

    championship_config, season = _get_discord_config(inter.guild_id)
    if what == 'presences':
        visual = 'presentation'
    elif what == 'vote_driveroftheday':
        visual = 'results'
    else:
        visual = what
    
    config = Reader(visual, championship_config, season, f'output/race_{what}.png', sheet_name).read()

    if what == 'presences':
        await PresenceEmbed.send_initial_messages(inter, config.race)
        return

    if what == 'vote_driveroftheday':
        race = config.race
        circuit_country = CIRCUIT_EMOJIS.get(race.circuit.city, f'({race.circuit.name})')
        await inter.followup.send(
            f"# Sondage pilote du jour course {race.round}\n"
            f"{race.circuit.city} {circuit_country}"
        )
        if config.grid_positions:
            msg_content = '`   Pos. Grille  Pilote`'
        else:
            msg_content = '`   Pos.  Pilote`'
        for index, pilot_data in config.ranking.iterrows():
            # Get pilot
            pilot_name = pilot_data[0]
            if not pilot_name:
                continue
            position = str(index+1)
            if len(position) == 1:
                position = f' {position}'
            if config.grid_positions:
                grid_position = config.grid_positions.get(pilot_name)
                if not grid_position:
                    grid_position_txt = ''
                else:
                    grid_position = str(grid_position)
                    if len(grid_position) == 1:
                        grid_position = f' {grid_position}'
                    grid_position_txt = f' (P{grid_position})  '
            else:
                grid_position_txt = ''
            msg_content += f'\n{VOTES_EMOJIS[index]} `{position}. {grid_position_txt} {pilot_name}`'
        msg = await inter.channel.send(msg_content)
        for emoji in VOTES_EMOJIS:
            await msg.add_reaction(emoji)
        return

    _logger.info('Rendering image...')
    output_filepath = Renderer.render(config, championship_config, season)
    if not output_filepath:
        await inter.followup.send('Le visuel était vide, êtes-vous sûr que le Sheet est bien rempli ?')
        return

    _logger.info('Sending image...')
    with open(output_filepath, 'rb') as f:
        picture = disnake.File(f)
        await inter.followup.send(file=picture)
        _logger.info('Image sent !')


@bot.slash_command(name="breaking", description='Breaking !')
async def breaking(inter,
                   img: disnake.Attachment = commands.Param(
                       name='img', description='Image utilisée comme fond de la breaking news'),
                   main_txt: str = commands.Param(name='main_txt', description='Texte principal de la breaking news'),
                   secondary_txt: str = commands.Param(
                       name='secondary_txt', description='Texte secondaire de la breaking news'),
                   team: str = commands.Param(name='team', default=None, choices=TEAMS,
                                              description="L'équipe concernée par la breaking news"),
                   background: str = commands.Param(
                       name='background', default='255,255,255', description="La couleur de fond à utiliser (au format R,G,B ou R,G,B,A), ignoré si le paramètre team est présent"),
                   foreground: str = commands.Param(
                       name='foreground', default='0,0,0', description="La couleur du texte (au format R,G,B ou R,G,B,A), ignoré si le paramètre team est présent"),
                   padding_top: int = commands.Param(
                       name='padding_top', default=None, description="L'espace en pixel à partir duquel l'image est collée en partant du haut. 0 pour tout en haut.")
                   ):
    _logger.info(f'{inter.user.display_name} called Breaking(main_txt={main_txt}, secondary_txt={secondary_txt}, team={team}, bg={background}, fg={foreground}, pt={padding_top})')
    await inter.response.defer()

    _logger.info('Rendering image...')
    input = (await img.to_file()).fp
    renderer = BreakingRenderer(main_txt, secondary_txt, team, background, foreground,
                                output='output/breaking.png', input=input, padding_top=padding_top)
    output_filepath = renderer.render()

    _logger.info('Sending image...')
    with open(output_filepath, 'rb') as f:
        picture = disnake.File(f)
        await inter.followup.send(file=picture)
        _logger.info('Image sent !')


@bot.slash_command(name="quote", description='Citation')
async def quote(inter,
                img: disnake.Attachment = commands.Param(
                    name='img', description='Image utilisée comme fond de la citation'),
                author: str = commands.Param(name='auteur', description='Auteur de la citation'),
                quote: str = commands.Param(
                    name='citation', description='Texte de la citation'),
                team: str = commands.Param(name='team', default=None, choices=TEAMS,
                                           description="L'équipe concernée par la citation"),
                background: str = commands.Param(
                    name='background', default='255,255,255', description="La couleur de fond à utiliser (au format R,G,B ou R,G,B,A), ignoré si le paramètre team est présent"),
                foreground: str = commands.Param(
                    name='foreground', default='0,0,0', description="La couleur du texte (au format R,G,B ou R,G,B,A), ignoré si le paramètre team est présent"),
                padding_top: int = commands.Param(
                    name='padding_top', default=None, description="L'espace en pixel à partir duquel l'image est collée en partant du haut. 0 pour tout en haut.")
                ):
    _logger.info(
        f'{inter.user.display_name} called Quote(author={author}, quote={quote}, team={team}, bg={background}, fg={foreground}, pt={padding_top})')
    await inter.response.defer()

    _logger.info('Rendering image...')
    input = (await img.to_file()).fp
    renderer = QuoteRenderer(quote, author, team, background, foreground,
                             output='output/quote.png', input=input, padding_top=padding_top)
    output_filepath = renderer.render()

    _logger.info('Sending image...')
    with open(output_filepath, 'rb') as f:
        picture = disnake.File(f)
        await inter.followup.send(file=picture)
        _logger.info('Image sent !')


@bot.slash_command(name="pilot", description='Pilot')
async def pilot(inter,
                   who: str = commands.Param(
                       name="name",
                       description="Le nom du pilote"
                   ),
                   visual_type: str = commands.Param(
                        name="visual_type",
                        choices=["lineup", 'closeup', 'whole'],
                        description="Type de visuel",
                        default='lineup'
                   ),
                   team: str = commands.Param(name='team', default=None, choices=TEAMS,
                                              description="L'équipe (celle de la saison actuelle par défaut)"),
                   ):
    _logger.info(f'{inter.user.display_name} called Pilot(who={who}, visual_type={visual_type}, team={team})')

    await inter.response.defer()

    try:
        championship_config, season = _get_discord_config(inter.guild_id)
        config = Reader('pilot', championship_config, season, f'output/pilot_{who}.png').read()
        _logger.info('Rendering image...')
        output_filepath = Renderer.render(config, championship_config, season, who, team=team, visual_type=visual_type)
        _logger.info('Sending image...')
        with open(output_filepath, 'rb') as f:
            picture = disnake.File(f)
            await inter.followup.send(file=picture)
            _logger.info('Image sent !')
    except PublicException as e:
        await inter.followup.send(str(e))


def _get_discord_config(discord_id:int) -> Tuple[Dict,str]:
    championship_config = DISCORDS[discord_id]
    _logger.info(f'Reading google sheet for {championship_config["name"]}')
    season = DISCORDS[discord_id]['current_season']
    return championship_config, season

async def _update_presence_message(guild_id, channel_id, message_id):
    channel = await bot.fetch_channel(channel_id)
    message = await channel.fetch_message(message_id)

    parts = message.content.split('\n')
    notified_role = parts[0]
    role = await _get_role_by_name(guild_id, notified_role)
    if not role:
        return

    pertinent_msg_reactions = (
        r for r in message.reactions if r.emoji in PRESENCE_EMOJIS
    )
    all_users = role.members
    mapping_users = {
        PRESENT_EMOJI: [],
        AWAY_EMOJI: [],
        'missing': []
    }
    for reaction in pertinent_msg_reactions:
        mapping_users[reaction.emoji] = [u.display_name async for u in reaction.users() if u in all_users]

    for user in all_users:
        if user.display_name not in mapping_users[PRESENT_EMOJI] and user.display_name not in mapping_users[AWAY_EMOJI]:
            mapping_users['missing'].append(user.display_name)

    # PRESENTS
    if len(mapping_users[PRESENT_EMOJI]) == 0:
        presents_str = '-'
    else:
        presents_str = ", ".join(mapping_users[PRESENT_EMOJI])
 
    # ABSENTS
    if len(mapping_users[AWAY_EMOJI]) == 0:
        away_str = '-'
    else:
        away_str = ", ".join(mapping_users[AWAY_EMOJI])
 
    # MISSINGS
    if len(mapping_users['missing']) == 0:
        missing_str = 'Tout le monde à voté !'
    else:
        missing_str = '❓Pas voté : ' + ", ".join(mapping_users["missing"])

#     msg = f"""{notified_role}

# {PRESENT_EMOJI} Présents : {presents_str}

# {AWAY_EMOJI} Absents : {away_str}

# ❓Pas voté : {missing_str}"""
#     msg = f"""{notified_role}

# {missing_str}"""
#     await message.edit(msg)

async def _get_role_by_name(guild_id, role_name):
    guild = bot.get_guild(guild_id)
    roles = await guild.fetch_roles()
    for r in roles:
        if r.mention == role_name:
            return r

## ERROR HANDLING

original_error_handler = bot.on_slash_command_error

async def on_slash_command_error(inter: disnake.ApplicationCommandInteraction, exception):
    what = inter.filled_options.get('what')
    await inter.delete_original_message()
    if what == 'results':
        await inter.channel.send("Une erreur est survenue dans la génération, êtes-vous sûr que la Google Sheet est bien remplie ? Si oui, contactez Xion.")
    else:
        await inter.channel.send('Une erreur est survenue dans la génération, contactez Xion.')
    _logger.exception(exception)
    await original_error_handler(inter, exception)

bot.on_slash_command_error = on_slash_command_error
