from typing import List
from src.telemetry.event import Event
from src.telemetry.message import Channel, Message
from src.telemetry.models.session import Session
from .abstract_listener import AbstractListener
from src.media_generation.data import circuits


class SessionCreationListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.SESSION_CREATED
    ]
    def _on_session_created(self, current: Session, old: Session)  -> List[Message]:
        circuit = circuits[current.track.get_name()]
        return [Message(content=f'# Début de la session "{current.session_type}" à {circuit.emoji} {current.track}', channel=Channel.BROADCAST)]
