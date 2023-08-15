from src.telemetry.models.session import Session
from .abstract_listener import AbstractListener


class SessionCreationListener(AbstractListener):
    def _on_session_created(self, old: Session, current: Session) -> str:
        return f'Début de la session "{current.session_type}" à {current.track}'
