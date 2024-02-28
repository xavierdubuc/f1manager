import logging
import disnake
from disnake.ext import commands

import src.bot.race_command as RaceCommand
import src.bot.rankings_command as RankingCommand
from src.media_generation.helpers.generator_type import GeneratorType

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

    # RACE i RESULTS
    if runtype == 'dry':
        results_channel = inter.channel
    else:
        results_channel = _get_channel(inter.bot, discord_config, 'results')
        await results_channel.send(f'# Résultats (provisoires) Course {race_config.race.round} {race_config.race.circuit.emoji}')
    await RaceCommand.run(inter, race_number, 'results', championship_config, season, results_channel)
    if runtype != 'dry':
        await inter.channel.send(f'✅ Résultats postés dans {results_channel.mention}!')

    # PILOTS RANKING
    if runtype == 'dry':
        pilots_ranking_channel = inter.channel
    else:
        pilots_ranking_channel = _get_channel(inter.bot, discord_config, 'pilots_ranking')
        await pilots_ranking_channel.send(f'# Classement provisoire après course {race_config.race.round} {race_config.race.circuit.emoji}')
    await RankingCommand.run(inter, 'pilots', 'Points', championship_config, season, pilots_ranking_channel)
    if runtype != 'dry':
        await inter.channel.send(f'✅ Classement pilotes posté dans {pilots_ranking_channel.mention}!')

    # TEAMS RANKING
    if runtype == 'dry':
        teams_ranking_channel = inter.channel
    else:
        teams_ranking_channel = _get_channel(inter.bot, discord_config, 'teams_ranking')
        await teams_ranking_channel.send(f'# Classement provisoire après course {race_config.race.round} {race_config.race.circuit.emoji}')
    await RankingCommand.run(inter, 'teams', 'Points', championship_config, season, teams_ranking_channel)
    if runtype != 'dry':
        await inter.channel.send(f'✅ Classement équipes posté dans {teams_ranking_channel.mention}!')

    if runtype != 'dry':
        drivervote_channel = _get_channel(inter.bot, discord_config, 'driver_vote')
        await RaceCommand.run(inter, race_number, 'vote_driveroftheday', championship_config, season, drivervote_channel)
        await inter.channel.send(f'✅ Sondage pour le pilote du jour posté dans {drivervote_channel.mention}!')

    round = int(race_number.split(' ')[0])
    next_round = round+1
    if runtype != 'dry':
        presences_channel = drivervote_channel = _get_channel(inter.bot, discord_config, 'presences')
        await RaceCommand.run(inter, next_round, 'presences', championship_config, season, presences_channel)
        await inter.channel.send(f'✅ Sondage de présence posté dans {presences_channel.mention}!')
        await inter.channel.send('Voilà, à la semaine prochaine !')
    else:
        await inter.channel.send(f'Le sondage de présence que je posterai sera celui de la course {next_round}')
