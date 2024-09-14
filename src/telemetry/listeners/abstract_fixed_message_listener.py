from dataclasses import dataclass
from typing import List

from src.telemetry.listeners.abstract_listener import AbstractListener
from src.telemetry.message import Channel, Message


@dataclass
class AbstractFixedMessageListener(AbstractListener):
    def _get_fixed_messages(self, *args, **kwargs) -> Message:
        msg_channel = self._get_fixed_message_channel(*args, **kwargs)
        msg_ids = self._get_fixed_messages_ids(*args, **kwargs)
        if msg_content_list := self._get_fixed_messages_content(*args, **kwargs):
            return [
                Message(msg_content, msg_channel, local_id=msg_id)
                for (msg_id, msg_content) in zip(msg_ids, msg_content_list)
            ]

    def _get_fixed_messages_content(self, *args, **kwargs) -> List[str]:
        return ["Pas encore de données"]

    def _get_fixed_message_channel(self, *args, **kwargs) -> Channel:
        return Channel.DEFAULT

    def _get_fixed_messages_ids(self, *args, **kwargs) -> List[str]:
        return []
