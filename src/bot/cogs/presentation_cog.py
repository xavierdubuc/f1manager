import disnake
from disnake.ext import commands
from src.bot.cogs.race_cog import RACE_NUMBER_PARAM, RaceCog


class PresentationCog(RaceCog):
    visual_type = 'presentation'

    @commands.slash_command(name="presentation", description='Présentation pour la course désirée')
    async def run(self, inter: disnake.ApplicationCommandInteraction,
                  race_number: str = RACE_NUMBER_PARAM, **kwargs):
        await super().run(inter, race_number, **kwargs)
