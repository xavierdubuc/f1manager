from dataclasses import dataclass

from src.telemetry.listeners.abstract_listener import AbstractListener
from src.telemetry.message import Channel, Message


@dataclass
class AbstractFixedMessageListener(AbstractListener):

    def _get_fixed_message(self, *args, **kwargs) -> Message:
        msg_id = self._get_fixed_message_id(*args, **kwargs)
        msg_channel = self._get_fixed_message_channel(*args, **kwargs)
        if msg_content := self._get_fixed_message_content(*args, **kwargs):
            return [Message(msg_content, msg_channel, local_id=msg_id)]

    def _get_fixed_message_content(self, *args, **kwargs) -> str:
        return "Pas encore de données"

    def _get_fixed_message_channel(self, *args, **kwargs) -> Channel:
        return Channel.DEFAULT

    def _get_fixed_message_id(self, *args, **kwargs) -> str:
        return None
