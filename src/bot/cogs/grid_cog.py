import disnake
from disnake.ext import commands
from src.bot.cogs.race_cog import RACE_NUMBER_PARAM, RaceCog


class GridCog(RaceCog):
    visual_type = 'grid'

    @commands.slash_command(name="grille", description='Grille de départ de la course désirée')
    async def run(self, inter: disnake.ApplicationCommandInteraction,
                  race_number: str = RACE_NUMBER_PARAM, **kwargs):
        await super().run(inter, race_number, **kwargs)
