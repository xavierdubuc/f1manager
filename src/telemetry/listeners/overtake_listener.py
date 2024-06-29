import logging
from typing import List
from src.telemetry.event import Event

from src.telemetry.message import Channel, Message
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from .abstract_listener import AbstractListener


class OvertakeListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.OVERTAKE
    ]

    def _on_overtake(self, overtaker: Participant, overtaken: Participant, session: Session) -> List[Message]:
        if not session.session_type.is_race():
            return None
        teamoji_1 = self.get_emoji(overtaker.team.as_emoji())
        teamoji_2 = self.get_emoji(overtaken.team.as_emoji())
        overtaker_lap = session.get_current_lap(overtaker)
        overtaken_lap = session.get_current_lap(overtaken)
        r_position = str(overtaker_lap.car_position).rjust(2)
        n_position = str(overtaken_lap.car_position).rjust(2)
        msg = f'`{r_position}` {teamoji_1} {overtaker} ⏩ `{n_position}` {teamoji_2} {overtaken}'
        return [Message(content=msg, channel=Channel.DEFAULT)]
