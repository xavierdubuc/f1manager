import asyncio
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


class ConfirmResultsCog(CompositeRaceCog):
    visual_type = 'results'

    @commands.slash_command(name="confirmation", description='Effectuer les actions nécessaires une fois le classement enterriné (après les sanctions éventuelles)')
    async def run(self, inter: disnake.ApplicationCommandInteraction,
                  race_number: str = RACE_NUMBER_PARAM, **kwargs):
        await super().run(inter, race_number, **kwargs)

    async def _run(self, channel: disnake.TextChannel, race_number: str, championship_config: dict, season: int, config: GeneratorConfig):
        discord_config = championship_config['discord']
        first_race_number, first_race_config, second_race_number, second_race_config = self._get_first_and_second_race_configs(
            race_number, config, championship_config, season)

        # DRIVER OF THE DAY : compute
        dotd_cog:DriverOfTheDayCog = self.bot.get_cog('DriverOfTheDayCog')
        if not second_race_config.race.driver_of_the_day:
            driver_of_the_day_name, percentage = await dotd_cog.compute(championship_config, second_race_config.race, season)
            await self.last_inter.channel.send(f'✅ Driver of the day calculé : {driver_of_the_day_name} ({percentage})')
            second_race_config.race.driver_of_the_day_name = driver_of_the_day_name
            second_race_config.race.driver_of_the_day = second_race_config.pilots[driver_of_the_day_name]
            second_race_config.race.driver_of_the_day_percent = percentage
        else:
            await self.last_inter.channel.send(f'Driver of the day déjà renseigné : {second_race_config.race.driver_of_the_day.name}')

        # RACE i RESULTS
        results_channel = self._get_channel(discord_config, 'results')
        results_cog:ResultsCog = self.bot.get_cog('ResultsCog')
        await results_cog._run(results_channel, first_race_number, championship_config, season, first_race_config, is_provisional=False)
        if first_race_number != second_race_number:
            await results_cog._run(results_channel, second_race_number, championship_config, season, second_race_config, is_provisional=False)
        await self.last_inter.channel.send(f'✅ Résultats postés dans {results_channel.mention}!')

        # DRIVER OF THE DAY : send
        await dotd_cog._run(results_channel, second_race_number, championship_config, season, second_race_config)
        await self.last_inter.channel.send(f'✅ Driver of the day posté dans {results_channel.mention}!')

        # RANKINGS
        ranking_cog: RankingCog = self.bot.get_cog('RankingCog')

        # \ PILOTS RANKING 
        pilots_ranking_channel = self._get_channel(discord_config, 'pilots_ranking')
        pilot_ranking_title = f'# Classement après course {second_race_config.race.round} {second_race_config.race.circuit.emoji}'
        await ranking_cog.pilots(pilots_ranking_channel, championship_config, season, pilot_ranking_title)
        await self.last_inter.channel.send(f'✅ Classement pilotes posté dans {pilots_ranking_channel.mention}!')

        # \ TEAMS RANKING
        teams_ranking_channel = self._get_channel(discord_config, 'teams_ranking')
        team_ranking_title = f'# Classement après course {second_race_config.race.round} {second_race_config.race.circuit.emoji}'
        await ranking_cog.teams(teams_ranking_channel, championship_config, season, team_ranking_title)
        await self.last_inter.channel.send(f'✅ Classement teams posté dans {teams_ranking_channel.mention}!')

        # \ LICENSE POINTS
        licenses_channel = self._get_channel(discord_config, 'license_points')
        last_message = await licenses_channel.fetch_message(licenses_channel.last_message_id)
        await last_message.delete()
        await ranking_cog.licenses(licenses_channel, championship_config, season)
        await self.last_inter.channel.send(f'✅ Permis posté dans {licenses_channel.mention}!')

