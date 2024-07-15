from dataclasses import dataclass

from src.telemetry.listeners.abstract_fixed_message_listener import AbstractFixedMessageListener


@dataclass
class AbstractTableAndMessageListener(AbstractFixedMessageListener):

    def _get_fixed_message_content(self, *args, **kwargs) -> str:
        elements = []
        if table := self._get_table(*args, **kwargs):
            elements.append(table)
        if last_update := self._get_update_message(*args, **kwargs):
            elements.append(last_update)
        return "\n".join(elements)

    def _get_table(self, *args, **kwargs) -> str:
        return ""

    def _get_update_message(self, *args, **kwargs) -> str:
        return ""
