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
    async def button_clicked(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
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
        for role_str in ('Titulaire', 'Réserviste', 'Commentateur'):
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

        inline = False
        for role in roles:
            embed.add_field(name=role.name, inline=inline, value='-')
            inline = True
        embed.add_field(name=AWAY_SECTION, inline=False, value='-')
        embed.add_field(name=VOTING_SECTION, inline=False, value='-')
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
        aways = [m for m in presences if presences[m] == 'N']
        presents = [m for m in presences if presences[m] == 'Y']
        didnt_votes = []
        didntvote_field = None
        for field in embed_dict['fields']:
            if field['name'].startswith(AWAY_SECTION):
                new_name = f'{AWAY_SECTION} ({len(aways)})'
                new_value = self._format_names(aways, field['inline'])
            else:
                real_field_name = field['name'].split('(')[0].strip()
                if real_field_name == VOTING_SECTION:
                    didntvote_field = field
                    continue
                else:
                    role = await self._get_role_by_name(real_field_name)
                    present_members = []
                    for m in role.members:
                        member_name = m.display_name
                        if member_name in presents:
                            present_members.append(member_name)
                        elif member_name not in aways:
                            didnt_votes.append(member_name)
                    new_value = self._format_names(present_members, field['inline'])
                    new_name = f'{real_field_name} ({len(present_members)})'
            if new_value and new_value != field['value']:
                field['value'] = new_value
                changed = True
            if new_name and new_name != field['name']:
                field['name'] = new_name
                changed = True

        if didnt_votes and didntvote_field:
            new_value = self._format_names(didnt_votes, didntvote_field['inline'])
            new_name = f'{real_field_name} ({len(didnt_votes)})'
            changed = True
            if new_value != didntvote_field['value']:
                didntvote_field['value'] = new_value
                changed = True
            if new_name and new_name != didntvote_field['name']:
                didntvote_field['name'] = new_name
                changed = True

        if changed:
            return embed_dict
        return None

    def _format_names(self, names: list, inline: bool):
        if not names:
            return '-'
        if inline:
            names_str = '\n'.join(names)
        else:
            middle = math.ceil(len(names)/2)
            table = []
            current_row = None
            for i, name in enumerate(names):
                if not current_row:
                    current_row = [name]
                    table.append(current_row)
                else:
                    current_row.append(name)
                    current_row = None
            names_str = tabulate(table, tablefmt='plain')
        return f'```\n{names_str}\n```'

    async def _get_role_by_name(self, role_str: str):
        for r in self.last_inter.guild.roles:
            if r.name == role_str:
                return r
        return None
