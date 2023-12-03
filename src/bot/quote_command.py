import logging
import disnake
from disnake.ext import commands
from quote import Renderer as QuoteRenderer
from src.media_generation.data import teams_idx

_logger = logging.getLogger(__name__)

TEAMS = list(teams_idx.keys())

IMG_PARAM = commands.Param(
    name='img',
    description='Image utilisée comme fond de la citation'
)
AUTHOR_PARAM = commands.Param(
    name='auteur',
    description='Auteur de la citation'
)
QUOTE_PARAM = commands.Param(
    name='citation',
    description='Texte de la citation'
)
TEAM_PARAM = commands.Param(
    name='team',
    default=None,
    choices=TEAMS,
    description="L'équipe concernée par la citation"
)
BG_PARAM = commands.Param(
    name='background',
    default='255,255,255',
    description="La couleur de fond à utiliser (au format R,G,B ou R,G,B,A), ignoré si le paramètre team est présent"
)
FG_PARAM = commands.Param(
    name='foreground',
    default='0,0,0',
    description="La couleur du texte (au format R,G,B ou R,G,B,A), ignoré si le paramètre team est présent"
)
PADDING_TOP_PARAM = commands.Param(
    name='padding_top',
    default=None,
    description="L'espace en pixel à partir duquel l'image est collée en partant du haut. 0 pour tout en haut."
)


async def run(
    inter: disnake.ApplicationCommandInteraction,
    img: disnake.Attachment,
    author: str,
    quote: str,
    team: str,
    background: str,
    foreground: str,
    padding_top: int
):
    _logger.info('Rendering image...')
    input = (await img.to_file()).fp
    renderer = QuoteRenderer(quote, author, team, background, foreground,
                             output='output/quote.png', input=input, padding_top=padding_top)
    output_filepath = renderer.render()

    _logger.info('Sending image...')
    with open(output_filepath, 'rb') as f:
        picture = disnake.File(f)
        await inter.followup.send(file=picture)
        _logger.info('Image sent !')
