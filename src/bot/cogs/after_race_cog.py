import disnake
from disnake.ext import commands
from src.bot.cogs.composite_race_cog import CompositeRaceCog
from src.bot.cogs.ranking_cog import RankingCog
from src.bot.cogs.presences_cog import PresencesCog
from src.bot.cogs.driver_of_the_day_cog import DriverOfTheDayCog
from src.bot.cogs.results_cog import ResultsCog
from src.media_generation.helpers.generator_type import GeneratorType
from src.media_generation.readers.race_reader_models.race import RaceType
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.bot.cogs.race_cog import RACE_NUMBER_PARAM, RaceCog


class AfterRaceCog(CompositeRaceCog):
    visual_type = 'results'

    @commands.slash_command(name="course_terminee", description='Effectuer les actions nécessaires une fois la course terminée')
    async def run(self, inter: disnake.ApplicationCommandInteraction,
                  race_number: str = RACE_NUMBER_PARAM, **kwargs):
        await super().run(inter, race_number, **kwargs)

    async def _run(self, channel: disnake.TextChannel, race_number: str, championship_config: dict, season: int, config: GeneratorConfig):
        discord_config = championship_config['discord']
        first_race_number, first_race_config, second_race_number, second_race_config = self._get_first_and_second_race_configs(
            race_number, config, championship_config, season)

        # RACE i RESULTS
        results_channel = self._get_channel(discord_config, 'results')
        results_cog:ResultsCog = self.bot.get_cog('ResultsCog')
        await results_cog._run(results_channel, first_race_number, championship_config, season, first_race_config, is_provisional=True)
        if first_race_number != second_race_number:
            await results_cog._run(results_channel, second_race_number, championship_config, season, second_race_config, is_provisional=True)
        await self.last_inter.channel.send(f'✅ Résultats postés dans {results_channel.mention}!')

        # RANKINGS
        ranking_cog: RankingCog = self.bot.get_cog('RankingCog')

        # \ PILOTS RANKING 
        pilots_ranking_channel = self._get_channel(discord_config, 'pilots_ranking')
        pilot_ranking_title = f'# Classement provisoire après course {second_race_config.race.round} {second_race_config.race.circuit.emoji}'
        await ranking_cog.pilots(pilots_ranking_channel, championship_config, season, pilot_ranking_title)
        await self.last_inter.channel.send(f'✅ Classement pilotes posté dans {pilots_ranking_channel.mention}!')

        # \ TEAMS RANKING
        teams_ranking_channel = self._get_channel(discord_config, 'teams_ranking')
        team_ranking_title = f'# Classement provisoire après course {second_race_config.race.round} {second_race_config.race.circuit.emoji}'
        await ranking_cog.teams(teams_ranking_channel, championship_config, season, team_ranking_title)
        await self.last_inter.channel.send(f'✅ Classement teams posté dans {teams_ranking_channel.mention}!')

        # DRIVER OF THE DAY
        vote_channel = self._get_channel(discord_config, 'driver_vote')
        dotd_cog:DriverOfTheDayCog = self.bot.get_cog('DriverOfTheDayCog')
        # await dotd_cog._run(vote_channel, second_race_number, championship_config, season, second_race_config)
        await dotd_cog._vote(vote_channel, second_race_config)
        await self.last_inter.channel.send(f'✅ Sondage pour le pilote du jour posté dans {vote_channel.mention}!')

        round = int(second_race_number.split(' ')[0])
        next_round = round+1
        if next_round > 12:
            await self.last_inter.channel.send("C'était la dernière course de la saison !")
            return

        # PRESENCES RACE i+1
        presences_channel = self._get_channel(discord_config, 'presences')
        presences_cog:PresencesCog = self.bot.get_cog('PresencesCog')
        await presences_cog.call(presences_channel, self.last_inter, next_round)
        await self.last_inter.channel.send(f'✅ Sondage de présence posté dans {presences_channel.mention}!')
        await self.last_inter.channel.send('Voilà, à la semaine prochaine !')

    def _get_channel(self, discord_config:dict, feed:str):
        config = discord_config[feed]
        guild = self.bot.get_guild(config['guild'])
        return guild.get_channel(config['chann'])
