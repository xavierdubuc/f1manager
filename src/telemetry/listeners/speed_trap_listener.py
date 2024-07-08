import logging
from typing import List

from src.telemetry.event import Event
from src.telemetry.message import Channel, Message
from src.telemetry.models.session import Session
from src.telemetry.models.speed_trap_entry import SpeedTrapEntry
from tabulate import tabulate

from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)

TABLE_FORMAT = "simple_outline"


class SpeedTrapListener(AbstractListener):
    SUBSCRIBED_EVENTS = [Event.SPEED_TRAP, Event.SESSION_ENDED]

    def _on_session_ended(self, session: Session) -> List[Message]:
        # TODO send classement
        pass

    def _on_speed_trap(self, speed_trap:SpeedTrapEntry, session: Session) -> List[Message]:
        key = speed_trap.participant
        existing_speedtrap = session.speed_traps.get(key)
        if not existing_speedtrap or existing_speedtrap < speed_trap:
            session.speed_traps[key] = speed_trap
            # TODO send a message when new speed trap ?
            # maybe send the classement also ? (with a local id so it can be edit)
        print(session.speed_traps)
        return []
