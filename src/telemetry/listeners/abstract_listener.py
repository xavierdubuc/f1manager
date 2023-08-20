from typing import List

from src.telemetry.message import Message
from ..event import Event


class AbstractListener:
    SUBSCRIBED_EVENTS = []

    def on(self, event:Event, *args, **kwargs) -> List[Message]:
        unsp_name = event.name.lower()
        method = getattr(self, f'_on_{unsp_name}')
        if method:
            res = method(*args, **kwargs)
            if not res:
                return res
            if not isinstance(res, list):
                return list(res)
