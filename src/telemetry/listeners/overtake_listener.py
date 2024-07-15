import logging
from typing import List
from src.telemetry.models.enums.pit_status import PitStatus
from src.telemetry.event import Event

from src.telemetry.message import Channel, Message
from src.telemetry.models.overtake import Overtake
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from .abstract_listener import AbstractListener


class OvertakeListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.OVERTAKE,
        Event.CLASSIFICATION_LIST_INITIALIZED,
    ]

    def _on_classification_list_initialized(self, session: Session, *args, **kwargs) -> List[Message]:
        if not session.session_type.is_race():
            return None
        msg = f"Total amount of overtakes : {len(session.overtakes)}"
        return [Message(content=msg, channel=Channel.DEFAULT)]

    def _on_overtake(self, overtaker: Participant, overtaken: Participant, session: Session) -> List[Message]:
        if not self._should_consider_overtake(overtaker, overtaken, session):
            return None
        session.overtakes.append(Overtake(
            overtaker=overtaker,
            overtaken=overtaken,
            lap_num=session.current_lap
        ))

        overtaken_lap = session.get_current_lap(overtaken)
        if overtaken_lap.pit_status != PitStatus.not_in_pit:
            return []

        msg = f'{self.driver(overtaker, session)} ⏩ {self.driver(overtaken, session)}'
        return [Message(content=msg, channel=Channel.DEFAULT)]

    def _should_consider_overtake(self, overtaker:Participant, overtaken:Participant, session:Session) -> bool:
        if not session.session_type.is_race():
            return False
        overtaken_lap = session.get_current_lap(overtaken)
        if overtaken_lap.pit_status != PitStatus.not_in_pit:
            return False
        # TODO implements Cid's restriction if possible
        return True
