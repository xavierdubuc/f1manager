import logging
from typing import Tuple

import disnake
from disnake.ext import commands
from src.gsheet.gsheet import GSheet
from src.media_generation.readers.race_reader_models.race import Race
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.helpers.generator_type import GeneratorType
from src.bot.cogs.race_cog import RACE_NUMBER_PARAM, RaceCog

VOTES_EMOJIS = '🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵🇶🇷🇸🇹'

_logger = logging.getLogger(__name__)


class DriverOfTheDayCog(RaceCog):
    visual_type = 'driver_of_the_day'

    @commands.slash_command(name="driver_of_the_day")
    async def root(self, inter: disnake.ApplicationCommandInteraction, **kwargs):
        pass

    @root.sub_command(name="calcul", description="Calcul du pilote du jour")
    async def compute_command(self, inter: disnake.ApplicationCommandInteraction,
                      race_number: str = RACE_NUMBER_PARAM, **kwargs):
        self._bootstrap(inter, race_number=race_number, **kwargs)
        championship_config, season = self._get_discord_config(inter.guild_id)
        race_config = self._read_config(race_number, 'results', GeneratorType.RESULTS, championship_config, season)
        await self.compute(championship_config, race_config.race, season)

    # TODO may be improved (pour l'instant ca choppe juste le dernier msg dans le channel)
    async def compute(self, championship_config: dict, race: Race, season: int=None) -> Tuple[str, int]:
        discord_config = championship_config['discord']
        channel = self._get_channel(discord_config, 'driver_vote')
        bot_messages = channel.history().filter(lambda m: m.author == self.bot.user and len(m.reactions) > 0)
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
        percentage = round((max_amount_of_vote / total_amount_of_vote), 2)
        dotd_pos = VOTES_EMOJIS.index(driver_of_the_day_emoji)
        driver_of_the_day = race.race_result.rows[dotd_pos].pilot_name
        g = GSheet()
        seasons = championship_config['seasons']
        season_id = season if season else championship_config['current_season']
        season = seasons[season_id]
        g.set_sheet_values(season['sheet'], f"'Race {race.round}'!I24:J24", [[
            driver_of_the_day, percentage
        ]])
        return driver_of_the_day, percentage

    @root.sub_command(name="results", description='Pilote du jour de la course désirée')
    async def run(self, inter: disnake.ApplicationCommandInteraction,
                  race_number: str = RACE_NUMBER_PARAM, **kwargs):
        await super().run(inter, race_number, **kwargs)

    @root.sub_command(name="vote", description='Démarrer le vote pour élire le pilote du jour de la course désirée')
    async def vote(self, inter: disnake.ApplicationCommandInteraction,
                   race_number: str = RACE_NUMBER_PARAM, **kwargs):
        await self._bootstrap(inter, race_number=race_number, **kwargs)
        championship_config, season = self._get_discord_config(inter.guild_id)
        config = self._read_config(race_number, 'results', GeneratorType.RESULTS, championship_config, season)
        await self._vote(inter.followup, config)

    async def _vote(self, channel: disnake.TextChannel, config: GeneratorConfig):
        _logger.info('Creating vote...')
        race = config.race
        circuit_country = race.circuit.emoji
        msg_content = (
            f"# Sondage pilote du jour course {race.round}\n"
            f"## {race.circuit.city} {circuit_country}\n"
        )
        if race.qualification_result:
            msg_content += '`   Pos. Grille  Pilote`'
        else:
            msg_content += '`   Pos.  Pilote`'
        for ranking_row in race.race_result.rows:
            # Get pilot
            if not ranking_row.pilot:
                continue
            position = ranking_row.position
            index = position - 1
            if len(str(ranking_row.position)) == 1:
                position = f' {position}'
            if race.qualification_result:
                qualification_res = race.qualification_result.get(ranking_row.pilot)
                if not qualification_res:
                    grid_position_txt = ''
                else:
                    grid_position = str(qualification_res.position)
                    if len(grid_position) == 1:
                        grid_position = f' {grid_position}'
                    grid_position_txt = f' (P{grid_position})  '
            else:
                grid_position_txt = ''
            msg_content += f'\n{VOTES_EMOJIS[index]} `{position}. {grid_position_txt} {ranking_row.pilot.name}`'
        msg = await channel.send(msg_content)
        for emoji in VOTES_EMOJIS[:len(race.race_result.rows)]:
            await msg.add_reaction(emoji)
