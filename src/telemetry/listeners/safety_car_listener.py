from typing import Dict, List
from src.telemetry.event import Event

from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Message
from src.telemetry.models.session import Session
from .abstract_listener import AbstractListener

class SafetyCarListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.SESSION_UPDATED
    ]
    def _on_session_updated(self, session:Session, changes:Dict[str, Change]) -> List[Message]:
        if 'safety_car_status' in changes:
            # emoji SC/VSC/drapeau jaune/rouge
            actual_status = changes['safety_car_status'].actual
            return [Message(content=str(actual_status))]
