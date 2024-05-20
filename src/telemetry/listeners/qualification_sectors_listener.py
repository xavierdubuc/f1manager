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

SECTOR_LENGTH = 10

class QualificationSectorsListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.LAP_CREATED,
        Event.LAP_UPDATED,
    ]

    def _on_lap_created(self, lap: Lap, participant: Participant, session: Session) -> List[Message]:
        # Only act if session is qualif and we have a lap record object
        lap_record = self._get_lap_record(participant, session)
        if not lap_record:
            _logger.info(f'[LAP_CREATED] No lap record found for {participant}')
            return []

        # Only act on last lap and if the last lap should not be ignored
        laps = session.get_laps(participant)
        last_lap = laps[-1]
        print(last_lap, last_lap.current_lap_time_in_ms)
        if len(laps) > 1:
            print(-2, laps[-2], laps[-2].current_lap_time_in_ms)

        if self._lap_should_be_ignored(last_lap):
            return []

        # Send last lap status only if last lap is completed and we have last lap sectors time
        if not lap.last_lap_time_in_ms or not last_lap.sector_1_time_in_ms or not last_lap.sector_2_time_in_ms:
            return []
        return [self._get_lap_repr(
            last_lap, lap.last_lap_time_in_ms, lap_record, participant, session
        )]

    def _on_lap_updated(self, lap: Lap, changes: Dict[str, Change], participant: Participant, session: Session) -> List[Message]:        
        # Only act if session is qualif and we have a lap record object
        lap_record = session.get_lap_record(participant)
        if not lap_record:
            _logger.info(f'[LAP_UPDATED] No lap record found for {participant}')
            return []
        
        if 'current_lap_invalid' in changes and lap.current_lap_invalid:
            return [self._get_lap_repr(lap, None, lap_record, participant, session)]
        if self._lap_should_be_ignored(lap):
            _logger.info(f'[LAP_UPDATED] {lap} of {participant} should be ignored')
            return []
        if 'sector_1_time_in_ms' not in changes and 'sector_2_time_in_ms' not in changes:
            return []
        return [self._get_lap_repr(lap, None, lap_record, participant, session)]

    def _get_lap_record(self, participant: Participant, session: Session) -> bool:
        if not session.session_type.is_qualification():
            return None
        return session.get_lap_record(participant)

    def _lap_should_be_ignored(self, lap: Lap) -> bool:
        return lap.current_lap_invalid or lap.driver_status != DriverStatus.flying_lap

    def _get_lap_repr(self, lap: Lap, lap_time: int, lap_record: LapRecord, participant: Participant, session: Session) -> Message:
        personal_best_lap = lap_record.best_lap_time
        overal_fastest_lap = session.current_fastest_lap
        delta_to_pole = personal_best_lap - overal_fastest_lap if (overal_fastest_lap and personal_best_lap) else None
        delta_to_pole_str = f' (+ {delta_to_pole})' if delta_to_pole else ''
        if lap.current_lap_invalid:
            details = '🟥🟥🟥 TOUR INVALIDE 🟥🟥🟥'
        else:
            current_s1 = lap.sector_1_time_in_ms
            current_s2 = lap.sector_2_time_in_ms
            current_s3 = lap_time
            personal_best_s1 =  lap_record.best_sector1_time
            personal_best_s2 =  lap_record.best_sector2_time
            personal_best_s3 =  lap_record.best_sector3_time

            delta_s1 = current_s1 - personal_best_s1 if (current_s1 and personal_best_s1) else None
            delta_s2 = current_s2 - personal_best_s2 if (current_s2 and personal_best_s2) else None
            delta_s3 = current_s3 - personal_best_s3 if (current_s3 and personal_best_s3) else None

            delta_s1_str = f'+ {self._format_time(delta_s1)}'.rjust(SECTOR_LENGTH) if delta_s1 else ' '*SECTOR_LENGTH
            delta_s2_str = f'+ {self._format_time(delta_s2)}'.rjust(SECTOR_LENGTH) if delta_s2 else ' '*SECTOR_LENGTH
            delta_s3_str = f'+ {self._format_time(delta_s3)}'.rjust(SECTOR_LENGTH) if delta_s3 else ' '*SECTOR_LENGTH
            current_s1_str = (self._format_time(current_s1) if current_s1 else '-:--.---').rjust(SECTOR_LENGTH)
            current_s2_str = (self._format_time(current_s2) if current_s2 else '-:--.---').rjust(SECTOR_LENGTH)
            current_s3_str = (self._format_time(current_s3) if current_s3 else '-:--.---').rjust(SECTOR_LENGTH)

            sep = ' '
            elements = [
                '```',
                sep.join((
                    f'LAP {lap.current_lap_num} S1'.rjust(SECTOR_LENGTH),
                    '    S2'.rjust(SECTOR_LENGTH),
                    '    S3'.rjust(SECTOR_LENGTH)
                )),
                sep.join((current_s1_str, current_s2_str,current_s3_str)),
            ]
            if delta_s1 or delta_s2 or delta_s3:
                elements.append(sep.join((delta_s1_str, delta_s2_str, delta_s3_str)))
            elements.append('```')
            details = '\n'.join(elements)
        msg = f'# `{str(lap.car_position).rjust(2)}` {participant} {personal_best_lap or "NO TIME SET"}{delta_to_pole_str}\n{details}'
        return self._create_message(msg, participant, lap)

    def _create_message(self, content:str, participant: Participant, lap: Lap):
        local_id = f'sectors_{participant.race_number}_lap{lap.current_lap_num}'
        print(local_id)
        return Message(content=content, channel=Channel.PACE, local_id=local_id)

    def _format_time(self, milliseconds:int):
        milliseconds = abs(milliseconds)
        if milliseconds == 0:
            return '0.000'

        full_seconds = milliseconds // 1000
        minutes = full_seconds // 60
        minutes_str = f'{minutes}:' if minutes > 0 else ''

        seconds = full_seconds % 60
        seconds_str = str(seconds).zfill(2) if minutes > 0 else seconds

        milliseconds = milliseconds % 1000
        milliseconds_str = str(milliseconds).zfill(3)

        return f'{minutes_str}{seconds_str}.{milliseconds_str}'
