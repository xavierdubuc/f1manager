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
        teamoji_1 = self.get_emoji(overtaker.team.as_emoji())
        teamoji_2 = self.get_emoji(overtaken.team.as_emoji())
        msg = f'{teamoji_1} {overtaker} ⏩ {teamoji_2} {overtaken}'
        return [Message(content=msg, channel=Channel.DEFAULT)]
