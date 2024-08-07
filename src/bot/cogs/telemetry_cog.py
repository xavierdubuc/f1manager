import logging

from disnake import TextChannel, File
from disnake.ext import commands, tasks
from src.telemetry.message import Channel, Message
from src.bot.vignebot import Vignebot

INTERVAL = 0.5

_logger = logging.getLogger(__name__)


class TelemetryCog(commands.Cog):
    def __init__(self, bot: Vignebot):
        self.bot = bot
        self.process_queue.start()
        self.sent_messages = {}

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild_id = self.bot.championship_config['discord']['default']['guild']
        self.guild = self.bot.get_guild(self.guild_id)
        emojis = self.guild.emojis
        setup_data = {
            'emojis': {e.name: str(e) for e in emojis}
        }
        self.bot.connection.send(setup_data)

    @tasks.loop(seconds=INTERVAL)
    async def process_queue(self):
        if not self.bot.queue:
            return
        while not self.bot.queue.empty():
            msg = self.bot.queue.get()
            await self._process(msg)

    @process_queue.before_loop
    async def before_process_queue(self):
        await self.bot.wait_until_ready()

    async def _process(self, msg: Message, initial_msg:Message=None):
        if not msg.channel:
            _logger.error(f'Cannot send "{msg.content} as it has no channel !')
            return
        if msg.channel == Channel.BROADCAST:
            await self._broadcast(msg)
            return

        _logger.info(f'Following msg ({len(msg)} chars) to be sent to Discord ({msg.channel})')
        _logger.info(msg.content)

        channel = self._get_channel_for(msg, is_broadcast=initial_msg is not None)
        if not channel:
            return

        if msg.is_empty():
            _logger.warning('Tried to send an empty message !')
            return

        await self._send_or_edit(msg, channel)

    async def _broadcast(self, msg: Message):
        channels = [c for c in Channel if c != Channel.BROADCAST]
        for channel in channels:
            await self._process(msg.copy(channel), msg)
        return

    async def _send_or_edit(self, msg: Message, channel: TextChannel):
        existing_message = False
        if msg.local_id:
            existing_message = self.sent_messages.get(msg.local_id)
            if not existing_message:
                _logger.info(f'Message with local id {msg.local_id} not found, sending a new one')
        kwargs = {'content': msg.get_content()}

        # FILE HANDLING
        if msg.file_path:
            with open(msg.file_path, 'rb') as f:
                picture = File(f)
                kwargs['file'] = picture

        # EDITION
        if existing_message:
            return await existing_message.edit(**kwargs)

        # CREATION
        message = await channel.send(**kwargs)
        if msg.local_id:
            self.sent_messages[msg.local_id] = message
        return message

    def _get_channel_for(self, msg: Message, is_broadcast=False):
        discord_config = self.bot.championship_config['discord'].get(msg.channel.value)
        if not discord_config:
            if is_broadcast:
                _logger.debug(f'Message will not be broadcasted on channel {msg.channel} as no specific config for it')
                return
            _logger.info(f'No discord config for {msg.channel}, will use default')
            discord_config = self.bot.championship_config['discord']['default']

        if is_broadcast and not discord_config.get('broadcast', True):
            _logger.debug(f'Message will not be broadcasted on channel {msg.channel} as no config does not allow it')
            return

        guild = self.bot.get_guild(discord_config['guild'])
        if not guild:
            _logger.error(f'Guild "{discord_config["guild"]}" not found, message not sent')
            return

        channel = guild.get_channel(discord_config['chann'])
        if not channel:
            for c in guild.channels:
                if c.name == discord_config['chann']:
                    channel = c
                    break
        if not channel:
            _logger.error(f'Channel "{discord_config["chann"]}" not found, message not sent')
            return

        _logger.info(f'Message sent to "{guild.name}/#{channel.name}"')
        return channel

