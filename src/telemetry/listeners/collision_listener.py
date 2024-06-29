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
        lap_1 = session.get_current_lap(participant_1)
        lap_2 = session.get_current_lap(participant_2)
        position_1 = str(lap_1.car_position).rjust(2)
        position_2 = str(lap_2.car_position).rjust(2)
        teamoji_1 = self.get_emoji(participant_1.team.as_emoji())
        teamoji_2 = self.get_emoji(participant_2.team.as_emoji())
        msg = f'`{position_1}` {teamoji_1} {participant_1} 💥 `{position_2}` {teamoji_2} {participant_2}'
        return [Message(content=msg, channel=Channel.DAMAGE)]
