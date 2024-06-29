import logging
from typing import List
from src.telemetry.event import Event

from src.telemetry.message import Channel, Message
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from .abstract_listener import AbstractListener


class CollisionListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.COLLISION
    ]

    def _on_collision(self, participant_1: Participant, participant_2: Participant, session: Session) -> List[Message]:
        teamoji_1 = self.get_emoji(participant_1.team.as_emoji())
        teamoji_2 = self.get_emoji(participant_2.team.as_emoji())
        msg = f'{teamoji_1} {participant_1} 💥 {teamoji_2} {participant_2}'
        return [Message(content=msg, channel=Channel.DAMAGE)]
