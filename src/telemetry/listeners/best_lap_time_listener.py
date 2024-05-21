import logging
from datetime import datetime, timedelta
from typing import Dict, List
from src.telemetry.event import Event

from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Channel, Message
from src.telemetry.models.lap_record import LapRecord
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from src.telemetry.models.weather_forecast import WeatherForecast
from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)


class BestLapTimeListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.LAP_RECORD_UPDATED
    ]

    def _on_lap_record_updated(self, lap_record:LapRecord, changes:Dict[str, Change], participant:Participant, session: Session)  -> List[Message]:
        if not changes or 'best_lap_time' not in changes:
            return []

        best_lap_time = changes["best_lap_time"].actual
        if best_lap_time == timedelta(0):
            return []

        lap_time = timedelta(seconds=best_lap_time/1000)
        formatted_lap_time = session._format_time(lap_time)
 
        # TODO add position of the pilot
        lap = session.get_current_lap(participant)
        position = str(lap.car_position).rjust(2)
        if not session.current_fastest_lap or best_lap_time < session.current_fastest_lap:
            if session.current_fastest_lap:
                difference = timedelta(seconds=(session.current_fastest_lap - best_lap_time)/1000)
                formatted_difference = f' (-{session._format_time(difference)})'
            else:
                formatted_difference = ''
            session.current_fastest_lap = best_lap_time
            session.current_fastest_lap_driver = participant
            session.current_fastest_lap_lap = session.current_lap
            msg = f'### 🕒 🟪 MEILLEUR TOUR 🟪 `{position}` {participant}  ` {formatted_lap_time}{formatted_difference}`'
        else:
            if changes["best_lap_time"].old:
                difference = timedelta(seconds=(changes["best_lap_time"].old - best_lap_time)/1000)
                formatted_difference = f' (-{session._format_time(difference)})'
            else:
                formatted_difference = ''
            if session.session_type.is_qualification() and session.current_fastest_lap:
                delta_p1 = timedelta(seconds=(best_lap_time-session.current_fastest_lap)/1000)
                formatted_delta_p1 = f' [+{session._format_time(delta_p1)}]'
            else:
                formatted_delta_p1 = ''
            msg = f'🕒 🟩 `{position}` **{participant}**  ` {formatted_lap_time}{formatted_difference}{formatted_delta_p1}`'

        return [Message(content=msg, channel=Channel.PACE)]
