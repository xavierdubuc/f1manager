import logging
from dataclasses import dataclass, field
from typing import Dict, List

from src.telemetry.message import Message

from ..event import Event

_logger = logging.getLogger(__name__)

@dataclass
class AbstractListener:
    emojis: Dict[str,str] = field(default_factory=dict)

    SUBSCRIBED_EVENTS = []

    def on(self, event:Event, *args, **kwargs) -> List[Message]:
        unsp_name = event.name.lower()
        method_name = f'_on_{unsp_name}'
        method = getattr(self, method_name)
        if method:
            res = method(*args, **kwargs)
            if res and not isinstance(res, list):
                return list(res)
            return res
        else:
            _logger.warning(f'{self.__class__.__name__}.{method_name} does not exist !')

    def get_emoji(self, emoji_name:str, str_if_not_found:str = None) -> str:
        return (self.emojis or {}).get(emoji_name, str_if_not_found or emoji_name)
