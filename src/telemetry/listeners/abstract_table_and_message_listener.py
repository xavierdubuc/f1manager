from dataclasses import dataclass
from typing import List

from src.telemetry.listeners.abstract_fixed_message_listener import AbstractFixedMessageListener


@dataclass
class AbstractTableAndMessageListener(AbstractFixedMessageListener):

    def _get_fixed_messages_content(self, *args, **kwargs) -> str:
        msg_content_list = []
        last_update = self._get_update_message(*args, **kwargs)
        if tables := self._get_tables(*args, **kwargs):
            for i, table in enumerate(i, tables):
                elements = [table]
                if last_update and i == len(tables) - 1:
                    elements.append(last_update)
                msg_content_list.append("\n".join(elements))
        return msg_content_list

    def _get_tables(self, *args, **kwargs) -> List[str]:
        return []

    def _get_update_message(self, *args, **kwargs) -> str:
        return ""
