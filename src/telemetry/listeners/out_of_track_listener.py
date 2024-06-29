import logging
from typing import Dict, List
from src.telemetry.models.enums.surface_type import SurfaceType
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
            amount_was_out_of_track = self._amount_of_rows_out_of_track(old_surfaces)
            amount_out_of_track = self._amount_of_rows_out_of_track(surfaces)

            is_on_track = amount_out_of_track > 1
            was_on_track = amount_was_out_of_track > 1
            if was_on_track and not is_on_track:
                if amount_out_of_track == 4:
                    msg = f"`{position}` {teamoji} {participant} est sorti de la piste !"
                elif amount_out_of_track == 3:
                    msg = f"`{position}` {teamoji} {participant} a mis 3 roues dehors !"
                elif amount_out_of_track == 2:
                    msg = f"`{position}` {teamoji} {participant} a mis 2 roues dehors !"
                else:
                    return
                _logger.info(f'{participant} : {surfaces}')
                return [Message(content=msg, channel=Channel.DEFAULT)]
            elif not was_on_track and is_on_track:
                msg = f"`{position}` {teamoji} {participant} est revenu sur la piste !"
                _logger.info(f'{participant} : {surfaces}')
                return [Message(content=msg, channel=Channel.DEFAULT)]

    def _amount_of_rows_out_of_track(self, surfaces:List[SurfaceType]) -> int:
        return sum(1 for surface in surfaces if not surface.is_on_track)
