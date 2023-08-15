from src.telemetry.event import Event
from src.telemetry.models.session import Session
from .abstract_listener import AbstractListener


class SessionCreationListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.SESSION_CREATED
    ]
    def _on_session_created(self, current: Session, old: Session) -> str:
        return f'Début de la session "{current.session_type}" à {current.track}'
