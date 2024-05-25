import logging

from twitchAPI.twitch import Twitch
from disnake.ext import commands, tasks
from src.bot.vignebot import Vignebot
from config import twitch_app_id, twitch_app_secret


INTERVAL = 120
FBRT_TWITCH_USER_ID = '756827903'
WATCHED_TWITCH_IDS = [FBRT_TWITCH_USER_ID]

_logger = logging.getLogger(__name__)


class TwitchCog(commands.Cog):
    def __init__(self, bot: Vignebot, guild_id:int, channel_id:int):
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.check_twitch_status.start()
        self.sent_messages = {}
        self.is_live = {}

    @tasks.loop(seconds=120)
    async def check_twitch_status(self):
        twitch = await Twitch(twitch_app_id, twitch_app_secret)
        _logger.info('Executing Twitch status check...')
        treated = {}
        async for stream in twitch.get_streams(user_id=WATCHED_TWITCH_IDS):
            _logger.info(f'{stream.user_name} is live !')
            treated[stream.user_id] = stream.user_name
            if stream.user_id not in self.is_live:
                self.is_live[stream.user_id] = stream.user_name
                channel = self.bot.get_guild(self.guild_id).get_channel(self.channel_id)
                msg = f'{stream.user_name} est en live, viens nous rejoindre sur https://twitch.tv/{stream.user_name.lower()} !'
                await channel.send(msg)
            else:
                _logger.info('... but already notified, just ignore it')

        _logger.info('Checking not treated watched twitch ids state...')
        for id in WATCHED_TWITCH_IDS:
            if id not in treated and id in self.is_live:
                live_name = self.is_live[id]
                _logger.info(f'{live_name} is no more live !')
                del self.is_live[id]
                channel = self.bot.get_guild(self.guild_id).get_channel(self.channel_id)
                msg = f'Le live de {live_name} est terminé, tu peux voir le replay sur https://twitch.tv/{live_name.lower()} !'
                await channel.send(msg)
        _logger.info('Done.')

    @check_twitch_status.before_loop
    async def before_process_queue(self):
        await self.bot.wait_until_ready()
