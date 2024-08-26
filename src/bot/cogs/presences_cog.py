import math
import disnake
from disnake.ext import commands
from tabulate import tabulate
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.gsheet.gsheet import PresenceGSheet
from src.bot.cogs.race_cog import RACE_NUMBER_PARAM, RaceCog

PRESENT_BUTTON_ID = 'present'
ABSENT_BUTTON_ID = 'absent'

VOTING_SECTION = 'Doit/doivent voter'
AWAY_SECTION = 'Absent(s)'
ADDITIONAL_SECTIONS = (AWAY_SECTION, VOTING_SECTION)

# TODO REFACTOR THAT SHIT
# IDEE : Liste des titulaires avec un ✅, un ❔(ou rien) ou un ❌
# Liste des réservistes : pareil
# chaque liste étant ordonné par présents en haut/absents en bas & puis par
# écurie ou ordre alphabétique. Afficher l'écurie éventuellement aussi ?
# style la "carte" comme dans grid ribbon ou dans results
# potentiellement utiliser le trigramme pour gagner de la place ?

class PresencesCog(RaceCog):
    visual_type = 'presentation'

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        self.last_inter = inter
        if inter.component.custom_id == PRESENT_BUTTON_ID:
            changed = await self._presence_clicked(inter, True)
        elif inter.component.custom_id == ABSENT_BUTTON_ID:
            changed = await self._presence_clicked(inter, False)
        if changed:
            await inter.followup.send(content="Merci pour ton vote !", ephemeral=True)

    async def _presence_clicked(self, inter: disnake.MessageInteraction, is_present: bool):
        embed = inter.message.embeds[0]
        race_name = embed.title
        championship_config, season = self._get_discord_config(inter.guild_id)
        gsheet = PresenceGSheet(championship_config['seasons'][season]['sheet'])
        gsheet.set(inter.user.display_name, race_name, is_present)
        embed_dict = await self._configure_embed(embed, inter)
        if embed_dict:
            await inter.message.edit(embed=disnake.Embed.from_dict(embed_dict))
        return bool(embed_dict)

    @commands.slash_command(name="presences", description='Lancer le sondage de présence pour la course désirée')
    async def run(self, inter: disnake.ApplicationCommandInteraction,
                  race_number: str = RACE_NUMBER_PARAM, **kwargs):
        await super().run(inter, race_number, **kwargs)

    async def _run(self, channel: disnake.TextChannel, race_number: str, championship_config: dict, season: int, config: GeneratorConfig):
        race = config.race
        inter = self.last_inter
        components = [
            disnake.ui.Button(label="Présent", style=disnake.ButtonStyle.green, custom_id=PRESENT_BUTTON_ID),
            disnake.ui.Button(label="Absent", style=disnake.ButtonStyle.red, custom_id=ABSENT_BUTTON_ID),
        ]
        circuit_country = race.circuit.emoji
        roles = []
        for role_str in ('Titulaire', 'Aspirant', 'Réserviste', 'Commentateur'):
            for r in inter.guild.roles:
                if r.name == role_str:
                    roles.append(r)

        embed = disnake.Embed(
            title=f"Course {race.round}",
            description=(
                f"## {race.circuit.city} {circuit_country}\n"
                f"*{race.full_date.strftime('%d/%m')} à {race.hour}*\n"
            )
        )
        # flag_path = race.circuit.get_assets_url('flags')
        # embed.set_thumbnail(file=disnake.File(flag_path))
        flag_path = f'http://xavierdubuc.com/public/circuits/flags/{race.circuit.id}.png'
        embed.set_thumbnail(url=flag_path)

        # photo_path = race.circuit.get_assets_url('photos')
        # embed.set_image(file=disnake.File(photo_path))
        photo_path = f'http://xavierdubuc.com/public/circuits/photos/{race.circuit.id}.png'
        embed.set_image(url=photo_path)

        for role in roles:
            inline = role.name not in ("Titulaire", "Commentateur")
            embed.add_field(name=role.name, inline=inline, value='-')
        embed_dict = await self._configure_embed(embed, inter)
        embed = disnake.Embed.from_dict(embed_dict)
        msg = f"{' '.join(r.mention for r in roles)}\nVeuillez voter !"
        await channel.send(msg, embed=embed, components=components)

    async def _configure_embed(self, embed: disnake.Embed, inter: disnake.ApplicationCommandInteraction):
        race_name = embed.title
        embed_dict = embed.to_dict()
        championship_config, season = self._get_discord_config(inter.guild_id)
        gsheet = PresenceGSheet(championship_config['seasons'][season]['sheet'])
        changed = False
        presences = gsheet.get(race_name)
        for field in embed_dict['fields']:
            real_field_name = field['name'].split('(')[0].strip()
            role = await self._get_role_by_name(real_field_name)
            amount_of_present_members = sum(1 for m in role.members if presences.get(m.display_name) == 'Y')
            new_value = self._format_names(role, presences, field['inline'])
            new_name = f'{real_field_name} ({amount_of_present_members})'
            if new_value and new_value != field['value']:
                field['value'] = new_value
                changed = True
            if new_name and new_name != field['name']:
                field['name'] = new_name
                changed = True

        if changed:
            return embed_dict
        return None

    def _format_names(self, role:disnake.Role, presences: dict, inline: bool):
        if not role.members:
            return '-'
        names_str_list = []
        for member in role.members:
            presence = presences.get(member.display_name,"")
            if presence == 'Y':
                emoji = '✅'
            elif presence == 'N':
                emoji = '❌'
            else:
                emoji = '❔'
            names_str_list.append(f'{emoji} {member.display_name}')
        names_str_list.sort(key=sorting_key)
        names_str = "\n".join(names_str_list)
        return f"```{names_str}```"

    async def _get_role_by_name(self, role_str: str):
        for r in self.last_inter.guild.roles:
            if r.name == role_str:
                return r
        return None

def sorting_key(name:str):
        if name.startswith('✅'):
            return 1
        elif name.startswith('❔'):
            return 2
        elif name.startswith('❌'):
            return 3
        return 4
