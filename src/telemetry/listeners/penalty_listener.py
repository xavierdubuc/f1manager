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
        teamoji = self.get_emoji(participant.team.as_emoji())
        if 'corner_cutting_warnings' in changes:
            amount_of_warnings = changes['corner_cutting_warnings'].actual
            msg = f'🏳️ {teamoji} **{participant}** a recu un avertissement ! **Total : {amount_of_warnings}**'
            messages.append(Message(content=msg, channel=Channel.PENALTY))
        if 'penalties' in changes:
            seconds_of_penalties = changes['penalties'].actual
            seconds_of_penalties_before = changes['penalties'].old
            diff = seconds_of_penalties - seconds_of_penalties_before
            if diff > 0:
                flagmoji = self.get_emoji('blackwhiteflag', '🏴')
                msg = f'{flagmoji} {teamoji} **{participant}** a recu une pénalité de {diff} secondes ! **Total : {seconds_of_penalties} secondes**'
            else:
                diff = -diff
                msg = f'✅ {teamoji} **{participant}** a purgé une pénalité de {diff} secondes ! **Total : {seconds_of_penalties} secondes**'
            messages.append(Message(content=msg, channel=Channel.PENALTY))
        return messages

