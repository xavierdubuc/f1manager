import disnake
from disnake.ext import commands
from src.bot.cogs.race_cog import RACE_NUMBER_PARAM, RaceCog


class LineupCog(RaceCog):
    visual_type = 'lineup'

    @commands.slash_command(name="lineup", description='Lineup pour la course désirée')
    async def run(self, inter: disnake.ApplicationCommandInteraction,
                  race_number: str = RACE_NUMBER_PARAM, **kwargs):
        await super().run(inter, race_number, **kwargs)

    def _get_title(self, race_number: str, championship_config: dict, season: int, config: dict):
        circuit_country = config.race.circuit.emoji
        return f'# Line-Up Course {config.race.round} {circuit_country}'
