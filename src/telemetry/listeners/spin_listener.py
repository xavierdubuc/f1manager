import logging
from typing import Dict

from src.telemetry.event import Event
from src.telemetry.managers.abstract_manager import Change
from src.telemetry.models.enums.original_driver import OriginalDriver
from src.telemetry.models.motion import Motion
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session

from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)

class SpinListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.MOTION_UPDATED,
    ]

    def _on_motion_updated(self, motion: Motion, changes: Dict[str, Change], participant: Participant, session: Session):
        if participant.original_driver == OriginalDriver.nico_hulkenberg:
            _logger.info(changes)
            _logger.warning(motion.yaw, motion.pitch, motion.roll)
