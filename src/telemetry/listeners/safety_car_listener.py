from typing import Dict
from src.telemetry.event import Event

from src.telemetry.managers.abstract_manager import Change
from .abstract_listener import AbstractListener

class SafetyCarListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.SESSION_UPDATED
    ]
    def _on_session_updated(self, session, changes:Dict[str, Change]) -> str:
        if 'safety_car_status' in changes:
            actual_status = changes['safety_car_status'].actual
            return str(actual_status)