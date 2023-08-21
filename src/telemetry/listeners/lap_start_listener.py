import logging
from datetime import datetime, timedelta
from typing import Dict, List
from src.telemetry.event import Event

from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Channel, Message
from src.telemetry.models.lap import Lap
from src.telemetry.models.lap_record import LapRecord
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from src.telemetry.models.weather_forecast import WeatherForecast
from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)


class LapStartListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.LAP_CREATED
    ]

    def _on_lap_created(self, lap: Lap, participant: Participant, session: Session) -> List[Message]:
        if session.session_type.is_race():
            if lap.car_position == 1:
                msg = f'#{lap.get_lap_num_title(session.total_laps)}'
            return [Message(content=msg, channel=Channel.DEFAULT)]
        return []
