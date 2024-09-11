import logging
from dataclasses import dataclass, field
from collections.abc import Iterable 
from typing import Dict, List

from src.telemetry.models.enums.tyre import Tyre
from src.telemetry.models.participant import Participant
from src.telemetry.message import Message
from src.telemetry.models.session import Session

from ..event import Event

_logger = logging.getLogger(__name__)


@dataclass
class AbstractListener:

    emojis: Dict[str, str] = field(default_factory=dict)

    SUBSCRIBED_EVENTS = []

    def on(self, event: Event, *args, **kwargs) -> List[Message]:
        unsp_name = event.name.lower()
        method_name = f'_on_{unsp_name}'
        method = getattr(self, method_name)
        if method:
            res = method(*args, **kwargs)
            if res and not isinstance(res, list):
                if isinstance(res, Iterable):
                    return list(res)
                return [res]
            return res
        else:
            _logger.warning(f'{self.__class__.__name__}.{method_name} does not exist !')

    def get_emoji(self, emoji_name: str, str_if_not_found: str = None) -> str:
        return (self.emojis or {}).get(emoji_name, str_if_not_found or emoji_name)

    def get_teamoji(self, participant: Participant):
        return self.get_emoji(participant.team.as_emoji()) if participant and participant.team else ''

    def get_tyremoji(self, tyre: Tyre):
        tyre_string = tyre.get_long_string()
        return self.get_emoji(tyre_string.lower(), tyre_string)

    def driver(self, participant: Participant, session: Session = None) -> str:
        elements = []
        # POSITION
        if session is not None:
            if lap := session.get_current_lap(participant):
                elements.append(f'`{str(lap.car_position).rjust(2)}`')

        # TEAMOJI
        if teamoji := self.get_teamoji(participant):
            elements.append(teamoji)

        # PARTICIPANT
        elements.append(str(participant))
        return ' '.join(elements)

    def tyre(self, tyre: Tyre, damage: int = None):
        tyre_emoji = self.get_tyremoji(tyre)
        if damage is None or damage == 0:
            tyre_damage = ''
        else:
            tyre_damage = f' ({damage} %)'
        return f'{tyre_emoji}{tyre_damage}'
