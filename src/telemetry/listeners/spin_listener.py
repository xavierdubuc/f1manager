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
            _logger.warning('------------------------------------------------------')
            _logger.warning(('POSITION :', round(motion.world_position_x, 2), round(motion.world_position_y, 2), round(motion.world_position_z, 2)))
            _logger.warning(('RIGHT  :', round(motion.world_right_dir_x, 2), round(motion.world_right_dir_y, 2), round(motion.world_right_dir_z, 2)))
            _logger.warning(('FORWARD  :', round(motion.world_forward_dir_x, 2), round(motion.world_forward_dir_y, 2), round(motion.world_forward_dir_z, 2)))
            _logger.warning(('VELOCITY  :', round(motion.world_velocity_x, 2), round(motion.world_velocity_y, 2), round(motion.world_velocity_z, 2)))
            _logger.warning(('G-FORCE  :', round(motion.g_force_lateral, 2), round(motion.g_force_longitudinal, 2), round(motion.g_force_vertical, 2)))
            _logger.warning(('YAPITCHROLL  :', round(motion.yaw, 2), round(motion.pitch, 2), round(motion.roll, 2)))
