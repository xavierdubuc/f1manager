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


class PenaltyListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.LAP_UPDATED
    ]

    def _on_lap_updated(self, lap: Lap, changes: Dict[str, Change], participant: Participant, session: Session) -> List[Message]:
        messages = []
        if 'warnings' in changes:
            amount_of_warnings = changes['warnings'].actual
            msg = f'🏳️  {participant} a recu un avertissement ! Total : {amount_of_warnings}'
            messages.append(Message(content=msg, channel=Channel.PENALTY))
        if 'penalties' in changes:
            seconds_of_penalties = changes['warnings'].actual
            seconds_of_penalties_before = changes['warnings'].old
            diff = seconds_of_penalties - seconds_of_penalties_before
            msg = f'🏴 {participant} a recu une pénalité de {diff} secondes ! Total : {seconds_of_penalties} secondes'
            messages.append(Message(content=msg, channel=Channel.PENALTY))
        return messages

