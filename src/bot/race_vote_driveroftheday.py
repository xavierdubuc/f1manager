import disnake

from src.media_generation.readers.race_reader_models.race import Race


VOTES_EMOJIS = '🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵🇶🇷🇸🇹'


async def send_initial_message(inter: disnake.MessageInteraction, race: Race):
    circuit_country = race.circuit.emoji
    await inter.followup.send(
        f"# Sondage pilote du jour course {race.round}\n"
        f"## {race.circuit.city} {circuit_country}"
    )
    if race.qualification_result:
        msg_content = '`   Pos. Grille  Pilote`'
    else:
        msg_content = '`   Pos.  Pilote`'
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
            grid_position = qualification_res.position
            if not grid_position:
                grid_position_txt = ''
            else:
                grid_position = str(grid_position)
                if len(grid_position) == 1:
                    grid_position = f' {grid_position}'
                grid_position_txt = f' (P{grid_position})  '
        else:
            grid_position_txt = ''
        msg_content += f'\n{VOTES_EMOJIS[index]} `{position}. {grid_position_txt} {ranking_row.pilot.name}`'
    print(msg_content)
    msg = await inter.channel.send(msg_content)
    for emoji in VOTES_EMOJIS:
        await msg.add_reaction(emoji)
