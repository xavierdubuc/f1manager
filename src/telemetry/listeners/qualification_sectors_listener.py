import logging
from datetime import datetime, timedelta
from typing import Dict, List
from src.telemetry.event import Event

from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Channel, Message
from src.telemetry.models.enums.driver_status import DriverStatus
from src.telemetry.models.lap import Lap
from src.telemetry.models.lap_record import LapRecord
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from src.telemetry.models.weather_forecast import WeatherForecast
from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)


class QualificationSectorsListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.LAP_CREATED,
        Event.LAP_UPDATED,
    ]

    def _on_lap_created(self, lap: Lap, participant: Participant, session: Session) -> List[Message]:
        if not session.session_type.is_qualification():
            return []
        lap_record = session.get_lap_record(participant)
        if not lap_record:
            return []
        last_lap = session.get_current_lap(participant)
        if self._lap_should_be_ignored(last_lap):
            return []

        # TODO idea to get the last posted message (one by participant/one by lap by participant)
        # and edit it instead of create a new one --> need to store posted messages
        return [
            self._get_sectors_message(
                last_lap, lap.last_lap_time_in_ms, lap_record, participant, session
            )
        ]

    def _on_lap_updated(self, lap: Lap, changes: Dict[str, Change], participant: Participant, session: Session) -> List[Message]:
        if not session.session_type.is_qualification():
            return []
        lap_record = session.get_lap_record(participant)
        if not lap_record:
            return []
        if self._lap_should_be_ignored(lap):
            return []
        if 'current_lap_invalid' in changes and lap.current_lap_invalid:
            square_repr = '🟥🟥🟥'
            return Message(content=f'**{participant}** : {square_repr}', channel=Channel.PACE)
        if 'sector1_time_in_ms' not in changes and 'sector2_time_in_ms' not in changes:
            return []
        return [
            self._get_sectors_message(
                lap, None, lap_record, participant, session
            )
        ]

    def _lap_should_be_ignored(self, lap: Lap) -> bool:
        return lap.current_lap_invalid or lap.driver_status in (DriverStatus.in_pit, DriverStatus.out_lap)

    def _get_sectors_message(self, lap: Lap, lap_time: int, lap_record: LapRecord, participant: Participant, session: Session) -> Message:
        pb_sector1 = lap_record.best_sector1_time
        ob_sector1 = session.current_fastest_sector1

        pb_sector2 = lap_record.best_sector2_time
        ob_sector2 = session.current_fastest_sector2

        pb_sector3 = lap_record.best_sector3_time
        ob_sector3 = session.current_fastest_sector3

        square_repr = lap.get_squared_repr(pb_sector1, ob_sector1, pb_sector2,
                                           ob_sector2, lap_time, pb_sector3, ob_sector3)
        msg = f'**{participant}** : {square_repr}'
        return Message(content=msg, channel=Channel.PACE)
