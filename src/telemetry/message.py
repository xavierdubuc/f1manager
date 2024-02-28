import logging
from dataclasses import dataclass

from disnake import File
_logger = logging.getLogger(__name__)


from enum import Enum
class Channel(Enum):
    BROADCAST = 'broadcast'
    DEFAULT = 'default'
    DAMAGE = 'damage'
    CLASSIFICATION = 'classification'
    WEATHER = 'weather'
    PACE = 'pace'
    PENALTY = 'penalty'
    PIT = 'pit'
    SETUP = 'setup'


@dataclass
class Message:
    content: str = None
    channel: Channel = Channel.DEFAULT
    file: File = None

    def get_content(self, force_full=False):
        if force_full or len(self.content) <= 2000:
            return self.content
        _logger.warning('Message is too long, returned content may be altered, below is the full message')
        _logger.warning(self.content)
        return self.content[:2000]

    def __len__(self):
        return len(self.content)
