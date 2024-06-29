import logging
from typing import Dict, List
from src.telemetry.models.telemetry import Telemetry
from src.telemetry.event import Event

from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Channel, Message

from src.telemetry.models.enums.pit_status import PitStatus
from src.telemetry.models.lap import Lap
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)


class OutOfTrackListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.TELEMETRY_UPDATED
    ]

    notified = {}

    def _on_telemetry_updated(self, telemetry:Telemetry, changes: Dict[str, Change], participant: Participant, session: Session) -> List[Message]:
        if 'surface_types' in changes:
            old_surfaces = changes['surface_types'].old
            surfaces = changes['surface_types'].actual
            teamoji = self.get_emoji(participant.team.as_emoji())
            lap = session.get_current_lap(participant)
            position = str(lap.car_position).rjust(2)
            is_on_track = all(surface.is_on_track() for surface in surfaces)
            was_on_track = all(surface.is_on_track() for surface in old_surfaces)
            if was_on_track and not is_on_track:
                msg = f"`{position}` {teamoji} {participant} est sorti de la piste !"
                _logger.info(f'{participant} : {surfaces}')
                return [Message(content=msg, channel=Channel.DEFAULT)]
            elif not was_on_track and is_on_track:
                msg = f"`{position}` {teamoji} {participant} est revenu sur la piste !"
                _logger.info(f'{participant} : {surfaces}')
                return [Message(content=msg, channel=Channel.DEFAULT)]
            