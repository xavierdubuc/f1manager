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


class QualificationSectorsListener(AbstractListener):  # FIXME could be a fixed table no ?
    SUBSCRIBED_EVENTS = [
        Event.LAP_CREATED,
        Event.LAP_UPDATED,
    ]

    def _on_lap_created(self, lap: Lap, participant: Participant, session: Session) -> List[Message]:
        # Only act if session is qualif and we have a lap record object
        lap_record = self._get_lap_record(participant, session)
        if not lap_record:
            return []

        # Only act on last lap and if the last lap should not be ignored
        laps = session.get_laps(participant)
        last_lap = laps[-1]

        if self._lap_should_be_ignored(last_lap):
            return []

        # Send last lap status only if last lap is completed and we have last lap sectors time
        if not lap.last_lap_time_in_ms or not last_lap.sector_1_time_in_ms or not last_lap.sector_2_time_in_ms:
            return []

        return [self._get_lap_repr(lap, lap_record, participant, session, last_lap)]

    def _on_lap_updated(self, lap: Lap, changes: Dict[str, Change], participant: Participant, session: Session) -> List[Message]:
        # Only act if session is qualif and we have a lap record object
        lap_record = session.get_lap_record(participant)
        if not lap_record:
            return []
        
        if 'current_lap_invalid' in changes and lap.current_lap_invalid:
            return [self._get_lap_repr(lap, lap_record, participant, session)]

        if self._lap_should_be_ignored(lap):
            return []

        if 'sector_1_time_in_ms' not in changes and 'sector_2_time_in_ms' not in changes:
            return []

        return [self._get_lap_repr(lap, lap_record, participant, session)]

    def _get_lap_record(self, participant: Participant, session: Session) -> bool:
        if not session.session_type.is_qualification():
            return None
        return session.get_lap_record(participant)

    def _lap_should_be_ignored(self, lap: Lap) -> bool:
        return lap.current_lap_invalid or lap.driver_status != DriverStatus.flying_lap or not lap.result_status.is_still_in_the_race()

    def _get_lap_repr(self, lap: Lap, lap_record: LapRecord, participant: Participant, session: Session, previous_lap: Lap = None) -> Message:
        personal_best_lap = lap_record.best_lap_time if lap_record else None
        overal_fastest_lap = session.current_fastest_lap
        lap_time = lap.last_lap_time_in_ms if previous_lap else None
        delta_to_pole = personal_best_lap - overal_fastest_lap if (overal_fastest_lap and personal_best_lap) else None
        delta_to_pole_str = f' ({self._format_time(delta_to_pole, True)})' if delta_to_pole else ''
        # current_lap contains the lap of which we are displaying the time
        # if previous lap is given, then it's that lap because lap is just given
        # to gain access to "last_lap_time_in_ms" and actual position
        current_lap = previous_lap or lap
        if not personal_best_lap:
            personal_best_lap = lap_time
        personal_best_lap_str = self._format_time(personal_best_lap) if personal_best_lap else '*No time set*'
        if current_lap.current_lap_invalid:
            details = '🟥🟥🟥 TOUR INVALIDE 🟥🟥🟥'
        else:
            current_s1 = current_lap.sector_1_time_in_ms
            current_s2 = current_lap.sector_2_time_in_ms
            current_s3 = (lap_time - current_s1 - current_s2) if lap_time else None
            personal_best_s1 =  lap_record.best_lap_sector1_time
            personal_best_s2 =  lap_record.best_lap_sector2_time
            personal_best_s3 =  lap_record.best_lap_sector3_time

            delta_s1 = current_s1 - personal_best_s1 if (current_s1 and personal_best_s1) else None
            delta_s2 = current_s2 - personal_best_s2 if (current_s2 and personal_best_s2) else None
            delta_s3 = current_s3 - personal_best_s3 if (current_s3 and personal_best_s3) else None
            delta_to_pb = lap_time - personal_best_lap if (lap_time and personal_best_lap) else None

            delta_s1_str = self._format_time(delta_s1, True).rjust(SECTOR_LENGTH) if delta_s1 else ' '*SECTOR_LENGTH
            delta_s2_str = self._format_time(delta_s2, True).rjust(SECTOR_LENGTH) if delta_s2 else ' '*SECTOR_LENGTH
            delta_s3_str = self._format_time(delta_s3, True).rjust(SECTOR_LENGTH) if delta_s3 else ' '*SECTOR_LENGTH
            delta_to_pb_str = self._format_time(delta_to_pb, True).rjust(SECTOR_LENGTH) if delta_to_pb else ' '*SECTOR_LENGTH
            current_s1_str = (self._format_time(current_s1) if current_s1 else '-:--.---').rjust(SECTOR_LENGTH)
            current_s2_str = (self._format_time(current_s2) if current_s2 else '-:--.---').rjust(SECTOR_LENGTH)
            current_s3_str = (self._format_time(current_s3) if current_s3 else '-:--.---').rjust(SECTOR_LENGTH)
            full_lap_str = (self._format_time(lap_time) if lap_time else '-:--.---').rjust(SECTOR_LENGTH)

            sep = ' '
            elements = [
                '```',
                sep.join((
                    '    S1'.rjust(SECTOR_LENGTH),
                    '    S2'.rjust(SECTOR_LENGTH),
                    '    S3'.rjust(SECTOR_LENGTH),
                    f'LAP {current_lap.current_lap_num}'.rjust(SECTOR_LENGTH),
                )),
                sep.join((current_s1_str, current_s2_str,current_s3_str, full_lap_str)),
            ]
            if delta_s1 or delta_s2 or delta_s3 or delta_to_pb_str:
                elements.append(f'{sep.join((delta_s1_str, delta_s2_str, delta_s3_str, delta_to_pb_str))}```')
            else:
                elements.append('```')
            details = '\n'.join(elements)
        teamoji = self.get_emoji(participant.team.as_emoji())
        msg = f'# `{str(lap.car_position).rjust(2)}` {teamoji} {participant} {personal_best_lap_str}{delta_to_pole_str}\n{details}'
        return self._create_message(msg, participant, current_lap)

    def _create_message(self, content:str, participant: Participant, lap: Lap):
        local_id = f'sectors_{participant.race_number}_lap{lap.index}'
        return Message(content=content, channel=Channel.PACE, local_id=local_id)

    def _format_time(self, signed_milliseconds:int, is_delta=False):
        milliseconds = abs(signed_milliseconds)
        if milliseconds == 0:
            return '0.000'

        full_seconds = milliseconds // 1000
        minutes = full_seconds // 60
        minutes_str = f'{minutes}:' if minutes > 0 else ''

        seconds = full_seconds % 60
        seconds_str = str(seconds).zfill(2) if minutes > 0 else seconds

        milliseconds = milliseconds % 1000
        milliseconds_str = str(milliseconds).zfill(3)
 
        if not is_delta:
            return f'{minutes_str}{seconds_str}.{milliseconds_str}'
        return f'{"-" if signed_milliseconds < 0 else "+"} {minutes_str}{seconds_str}.{milliseconds_str}'
