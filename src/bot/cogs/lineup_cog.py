import disnake
from disnake.ext import commands
from src.bot.cogs.race_cog import RACE_NUMBER_PARAM, RaceCog


class LineupCog(RaceCog):
    visual_type = 'lineups'

    @commands.slash_command(name="lineup", description='Lineup pour la course désirée')
    async def run(self, inter: disnake.ApplicationCommandInteraction,
                  race_number: str = RACE_NUMBER_PARAM, **kwargs):
        await super().run(inter, race_number, **kwargs)

    async def _send_title(self, channel: disnake.TextChannel, race_number: str, championship_config: dict, season: int, config: dict):
        circuit_country = config.race.circuit.emoji
        await channel.send(f'# Line-Up Course {config.race.round} {circuit_country}')
