import logging
from typing import Dict, Tuple
import disnake
from disnake.ext import commands
from datetime import datetime

from src.media_generation.helpers.reader import Reader
from src.media_generation.helpers.general_ranking_reader import GeneralRankingReader
from src.media_generation.helpers.renderer import Renderer

from breaking import Renderer as BreakingRenderer
from quote import Renderer as QuoteRenderer

from src.media_generation.data import teams_idx
from config import DISCORDS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

_logger = logging.getLogger(__name__)
TEAMS = list(teams_idx.keys())

PRESENT_EMOJI = '✅'
AWAY_EMOJI = '❌'
PRESENCE_EMOJIS = [PRESENT_EMOJI, AWAY_EMOJI]

command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True

intents = disnake.Intents.default()
intents.members = True
bot = commands.InteractionBot(command_sync_flags=command_sync_flags, intents=intents)

FBRT_GUILD_ID = 923505034778509342
FBRT_BOT_CHAN_ID = 1074632856443289610
DEBUG_GUILD_ID = 1074380392154533958
DEBUG_CHAN_ID = 1096169137589461082


@bot.event
async def on_ready():
    msg = f'Mesdames messieurs {"bonjour" if 5 < datetime.now().hour < 17 else "bonsoir"} !'
    # await bot.get_guild(DEBUG_GUILD_ID).get_channel(DEBUG_CHAN_ID).send(msg, tts=True)
    _logger.info('Connected !')


@bot.event
async def on_message(msg: disnake.Message):
    if bot.user.mentioned_in(msg) and not msg.mention_everyone and msg.type != disnake.MessageType.reply:
        # TODO calepino
        await msg.channel.send("Vous m'avez appelé ? Ne vous en faites Gaëtano est là ! J'vous ai déjà parlé de mon taximan brésilien ?")

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.emoji.name in PRESENCE_EMOJIS:
        await _update_presence_message(payload.guild_id, payload.channel_id, payload.message_id, payload.emoji.name)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    if payload.emoji.name == '💥':
        channel = await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author == bot.user:
            await message.delete()
        return
    if payload.emoji.name in PRESENCE_EMOJIS:
        await _update_presence_message(payload.guild_id, payload.channel_id, payload.message_id, payload.emoji.name)


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
               what: str = commands.Param(name="what", choices=[
                                          'presences', 'presentation', 'lineup', 'results', 'grid_ribbon'])
               ):
    _logger.info(f'{inter.user.display_name} called Race(race_number={race_number}, what={what})')
    sheet_name = f'Race {race_number}'
    await inter.response.defer()

    championship_config, season = _get_discord_config(inter.guild_id)
    visual = what if what != 'presences' else 'presentation'
    config = Reader(visual, championship_config, season, f'output/race_{what}.png', sheet_name).read()

    if what == 'presences':
        race = config.race
        await inter.followup.send(
            f"# Présences course {race.round}\n"
            f"{race.full_date.strftime('%d/%m')} à {race.hour}\n"
            f"{race.circuit.city} ({race.circuit.name})"
        )
        for role_str in ('Titulaire', 'Réserviste', 'Commentateur'):
            role = None
            for r in inter.guild.roles:
                if r.name == role_str:
                    role = r
            if role:
                msg = await inter.channel.send(role.mention)
                await msg.add_reaction(PRESENT_EMOJI)
                await msg.add_reaction(AWAY_EMOJI)
            else:
                _logger.error(f'Role {role_str} not found !')
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

def _get_discord_config(discord_id:int) -> Tuple[Dict,str]:
    championship_config = DISCORDS[discord_id]
    _logger.info(f'Reading google sheet for {championship_config["name"]}')
    season = DISCORDS[discord_id]['current_season']
    return championship_config, season

async def _update_presence_message(guild_id, channel_id, message_id, emoji):
    channel = await bot.fetch_channel(channel_id)
    message = await channel.fetch_message(message_id)

    parts = message.content.split('\n')
    notified_role = parts[0]
    role = await _get_role_by_name(guild_id, notified_role)

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
        missing_str = ", ".join(mapping_users["missing"])

    msg = f"""{notified_role}

{PRESENT_EMOJI} Présents : {presents_str}

{AWAY_EMOJI} Absents : {away_str}

❓Pas voté : {missing_str}"""
    await message.edit(msg)

async def _get_role_by_name(guild_id, role_name):
    guild = bot.get_guild(guild_id)
    roles = await guild.fetch_roles()
    for r in roles:
        if r.mention == role_name:
            return r

# def _get_

## ERROR HANDLING

original_error_handler = bot.on_slash_command_error

async def on_slash_command_error(inter: disnake.ApplicationCommandInteraction, exception):
    what = inter.filled_options.get('what')
    await inter.delete_original_message()
    if what in ('results', 'fastest'):
        await inter.channel.send("Une erreur est survenue dans la génération, êtes-vous sûr que la Google Sheet est bien remplie ? Si oui, contactez Xion.")
    else:
        await inter.channel.send('Une erreur est survenue dans la génération, contactez Xion.')
    _logger.exception(exception)
    await original_error_handler(inter, exception)

bot.on_slash_command_error = on_slash_command_error
