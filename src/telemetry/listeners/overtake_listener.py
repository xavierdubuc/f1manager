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
        Event.OVERTAKE,
        Event.SESSION_ENDED
    ]

    def _on_session_ended(self, session:Session) -> List[Message]:
        msg = f"Total amount of overtakes : {len(session.overtakes)}"
        return [Message(content=msg, channel=Channel.DEFAULT)]

    def _on_overtake(self, overtaker: Participant, overtaken: Participant, session: Session) -> List[Message]:
        if not session.session_type.is_race():
            return None
        if self._should_consider_overtake(overtaker, overtaken, session):
            session.overtakes += (overtaker, overtaken) # add lap ?

        teamoji_overtaken = self.get_emoji(overtaken.team.as_emoji())
        overtaken_lap = session.get_current_lap(overtaken)
        if overtaken_lap.pit_status != PitStatus.not_in_pit:
            return []

        overtaker_lap = session.get_current_lap(overtaker)
        n_position = str(overtaken_lap.car_position).rjust(2)
        teamoji_overtaker = self.get_emoji(overtaker.team.as_emoji())
        r_position = str(overtaker_lap.car_position).rjust(2)
        msg = f'`{r_position}` {teamoji_overtaker} {overtaker} ⏩ `{n_position}` {teamoji_overtaken} {overtaken}'
        return [Message(content=msg, channel=Channel.DEFAULT)]

    def _should_consider_overtake(self, overtaker:Participant, overtaken:Participant, session=Session) -> bool:
        return True # implements Cid's restriction if possible
