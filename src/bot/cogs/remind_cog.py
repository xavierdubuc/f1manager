import disnake
from disnake.ext import commands
from src.bot.cogs.vignebot_cog import VignebotCog
from src.gsheet.gsheet import PresenceGSheet
from src.bot.cogs.race_cog import RACE_NUMBER_PARAM, RaceCog

from logging import getLogger
_logger = getLogger(__name__)

ROLES = ('Titulaire', 'Aspirant', 'Réserviste', 'Commentateur')
ROLE_PARAM = commands.Param(
    name="role",
    description='Le rôle à notifier',
    default=None,
    choices=list(ROLES)
)


class RemindCog(VignebotCog):
    @commands.slash_command(name="notifier")
    async def root(self, inter: disnake.ApplicationCommandInteraction, **kwargs):
        pass

    @root.sub_command(name="pilote_du_jour", description="Rappeler de voter pour le pilote du jour")
    async def vote_for_dotd(self, inter: disnake.ApplicationCommandInteraction, **kwargs):
        await self._bootstrap(inter)
        championship_config, season = self._get_discord_config(inter.guild_id)
        discord_config = championship_config['discord']
        remind_channel = self._get_channel(discord_config, 'reminder')
        driver_vote_channel = self._get_channel(discord_config, 'driver_vote')
        msg = f"{inter.guild.roles[0].mention} n'oubliez pas de voter pour le pilote du jour dans {driver_vote_channel.mention} !"
        if remind_channel != inter.channel:
            await inter.followup.send("C'est fait :)")
            await remind_channel.send(msg)
        else:
            await inter.followup.send(msg)

    @root.sub_command(name="presence", description="Rappeler à ceux dont ce n'est pas encore le cas de remplir leur présence")
    async def presence(self, inter: disnake.ApplicationCommandInteraction,
                       race_number: str = RACE_NUMBER_PARAM,
                       only_role: str = ROLE_PARAM,
                       **kwargs):
        await self._bootstrap(inter)
        race_name = f'Course {race_number}'
        championship_config, season = self._get_discord_config(inter.guild_id)
        discord_config = championship_config['discord']
        presences_channel = self._get_channel(discord_config, 'presences')
        gsheet = PresenceGSheet(championship_config['seasons'][season]['sheet'])
        presences = gsheet.get(race_name)

        didnt_vote = []
        roles = championship_config["roles"] if only_role is None else [only_role]
        for role in inter.guild.roles:
            if role.name in roles:
                for member in role.members:
                    presence = presences.get(member.display_name, "")
                    if presence not in ('Y', 'N'):
                        didnt_vote.append(member)

        msg = f"☝️ {' '.join(m.mention for m in didnt_vote)} ☝️"
        if presences_channel != inter.channel:
            await inter.followup.send("C'est fait :)")
            await presences_channel.send(msg)
        else:
            await inter.followup.send(msg)
