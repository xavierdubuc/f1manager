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


class PositionChangeListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.LAP_START_CREATED
    ]

    def _on_lap_start_created(self, lap: Lap, participant: Participant, session: Session, previous_lap: Lap = None) -> List[Message]:
        if not session.session_type.is_race():
            return []
        if not previous_lap or previous_lap.car_position == lap.car_position:
            return []
        position_change = lap.get_position_evolution(previous_lap)
        if position_change:
            return [Message(content=f'{position_change} **{participant}**', channel=Channel.DEFAULT)]
