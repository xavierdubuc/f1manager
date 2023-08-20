from typing import List
from src.telemetry.event import Event
from src.telemetry.message import Channel, Message
from src.telemetry.models.session import Session
from .abstract_listener import AbstractListener


class SessionCreationListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.SESSION_CREATED
    ]
    def _on_session_created(self, current: Session, old: Session)  -> List[Message]:
        return [Message(content=f'Début de la session "{current.session_type}" à {current.track}', channel=Channel.BROADCAST)]
