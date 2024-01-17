import logging
import disnake
from disnake.ext import commands

import src.bot.race_command as RaceCommand
from src.bot.race_vote_driveroftheday import VOTES_EMOJIS
import src.bot.rankings_command as RankingCommand
from src.media_generation.helpers.generator_type import GeneratorType
from src.media_generation.readers.race_reader_models.race import Race
from src.gsheet.gsheet import GSheet

_logger = logging.getLogger(__name__)


RUNTYPE_PARAM = commands.Param(
    name="run_type",
    choices=["dry", 'final'],
    description="Type de run",
    default='dry'
)

def _get_channel(bot: commands.InteractionBot, discord_config:dict, feed:str):
    config = discord_config[feed]
    guild = bot.get_guild(config['guild'])
    return guild.get_channel(config['chann'])

async def _compute_driver_of_the_day(bot: commands.InteractionBot, championship_config:dict, race:Race):
    discord_config = championship_config['discord']
    channel = _get_channel(bot, discord_config, 'driver_vote')
    bot_messages = channel.history().filter(lambda m:m.author==bot.user and len(m.reactions) > 0)
    sondage_msg = (await bot_messages.flatten())[0]
    reactions = [r for r in sondage_msg.reactions if r.count > 1]
    driver_of_the_day_emoji = None
    total_amount_of_vote = 0
    max_amount_of_vote = 0
    for r in reactions:
        count = r.count - 1
        if count > max_amount_of_vote:
            driver_of_the_day_emoji = r.emoji
            max_amount_of_vote = count
        total_amount_of_vote += count
    percentage = round((max_amount_of_vote / total_amount_of_vote),2)
    dotd_pos = VOTES_EMOJIS.index(driver_of_the_day_emoji)
    driver_of_the_day = race.race_result.rows[dotd_pos].pilot_name
    g = GSheet()
    seasons = championship_config['seasons']
    season_id = list(seasons.keys())[-1]
    season = seasons[season_id]
    g.set_sheet_values(season['sheet'], f"'Race {race.round}'!I24:J24", [[
        driver_of_the_day, percentage
    ]])

async def run(
        inter: disnake.ApplicationCommandInteraction,
        runtype: str,
        race_number: str,
        championship_config: dict,
        season: int):
    if runtype == 'dry':
        await inter.followup.send("Ok, Gaëtano va vous montrer !")
    else:
        await inter.followup.send("Ok, laissez faire Gaëtano !")
    discord_config = championship_config['discord']
    race_config = RaceCommand.read_config(race_number, 'results', GeneratorType.RESULTS, championship_config, season)
    await _compute_driver_of_the_day(inter.bot, championship_config, race_config.race)

    # RACE RESULTS
    if runtype == 'dry':
        results_channel = inter.channel
    else:
        results_channel = _get_channel(inter.bot, discord_config, 'results')
        await results_channel.send(f'# Résultats Course {race_config.race.round} {race_config.race.circuit.emoji}')
    await RaceCommand.run(inter, race_number, 'results', championship_config, season, results_channel)
    await RaceCommand.run(inter, race_number, 'driver_of_the_day', championship_config, season, results_channel)
    if runtype != 'dry':
        await inter.channel.send(f'✅ Résultats & Driver of the day postés dans {results_channel.mention}!')

    # PILOTS RANKING
    if runtype == 'dry':
        pilots_ranking_channel = inter.channel
    else:
        pilots_ranking_channel = _get_channel(inter.bot, discord_config, 'pilots_ranking')
        await pilots_ranking_channel.send(f'# Classement après course {race_config.race.round} {race_config.race.circuit.emoji}')
    await RankingCommand.run(inter, 'pilots', 'Points', championship_config, season, pilots_ranking_channel)
    if runtype != 'dry':
        await inter.channel.send(f'✅ Classement pilotes posté dans {pilots_ranking_channel.mention}!')

    # TEAMS RANKING
    if runtype == 'dry':
        teams_ranking_channel = inter.channel
    else:
        teams_ranking_channel = _get_channel(inter.bot, discord_config, 'teams_ranking')
        await teams_ranking_channel.send(f'# Classement après course {race_config.race.round} {race_config.race.circuit.emoji}')
    await RankingCommand.run(inter, 'teams', 'Points', championship_config, season, teams_ranking_channel)
    if runtype != 'dry':
        await inter.channel.send(f'✅ Classement équipes posté dans {teams_ranking_channel.mention}!')

    # LICENSE POINTS
    if runtype == 'dry':
        license_points = inter.channel
    else:
        license_points = _get_channel(inter.bot, discord_config, 'license_points')
        last_message = await license_points.fetch_message(license_points.last_message_id)
        await last_message.delete()
    await RankingCommand.run(inter, 'license_points', 'Points', championship_config, season, license_points)
    if runtype != 'dry':
        await inter.channel.send(f'✅ Permis postés dans {license_points.mention}!')

