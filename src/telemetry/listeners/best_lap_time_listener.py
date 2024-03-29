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
        lap_time = timedelta(seconds=best_lap_time/1000)
        formatted_lap_time = session._format_time(lap_time)

        if not session.current_fastest_lap or best_lap_time < session.current_fastest_lap:
            session.current_fastest_lap = best_lap_time
            msg = f'### 🕒 🟪 MEILLEUR TOUR 🟪  {participant}  ` {formatted_lap_time} `'
        else:
            msg = f'🕒 🟩  **{participant}**  ` {formatted_lap_time} `'

        return [Message(content=msg, channel=Channel.PACE)]