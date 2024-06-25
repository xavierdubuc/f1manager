from dataclasses import dataclass, field
from typing import Dict, List

from src.telemetry.message import Message
from ..event import Event

@dataclass
class AbstractListener:
    emojis: Dict[str,str] = field(default_factory=dict)

    SUBSCRIBED_EVENTS = []

    def on(self, event:Event, *args, **kwargs) -> List[Message]:
        unsp_name = event.name.lower()
        method = getattr(self, f'_on_{unsp_name}')
        if method:
            res = method(*args, **kwargs)
            if res and not isinstance(res, list):
                return list(res)
            return res

    def get_emoji(self, emoji_name:str, str_if_not_found:str = None) -> str:
        return (self.emojis or {}).get(emoji_name, str_if_not_found or emoji_name)
