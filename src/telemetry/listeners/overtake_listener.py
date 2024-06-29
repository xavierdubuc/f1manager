import logging
from typing import List
from src.telemetry.models.enums.pit_status import PitStatus
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
        # TODO COUNT OVERTAKES ON SESSION (maybe try to implement restriction from CID)
        teamoji_overtaken = self.get_emoji(overtaken.team.as_emoji())
        overtaken_lap = session.get_current_lap(overtaken)
        if overtaken_lap.pit_status != PitStatus.not_in_pit:
            return []

        n_position = str(overtaken_lap.car_position).rjust(2)
        teamoji_overtaker = self.get_emoji(overtaker.team.as_emoji())
        r_position = str(overtaker_lap.car_position).rjust(2)
        overtaker_lap = session.get_current_lap(overtaker)
        msg = f'`{r_position}` {teamoji_overtaker} {overtaker} ⏩ `{n_position}` {teamoji_overtaken} {overtaken}'
        return [Message(content=msg, channel=Channel.DEFAULT)]
