import logging
from dataclasses import dataclass
from typing import Dict, List

from src.telemetry.event import Event
from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Channel, Message
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from src.telemetry.models.telemetry import Telemetry

from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)

PARTICIPANTS_TO_MONITOR = ["FBRT_Sepheldor", "STROLL"]


@dataclass
class TyreTemperatureListener(AbstractListener):
    max_values = {}

    SUBSCRIBED_EVENTS = [
        Event.TELEMETRY_UPDATED,
    ]

    notified = {}

    def _on_telemetry_updated(self, telemetry: Telemetry, changes: Dict[str, Change], participant: Participant, session: Session) -> List[Message]:
        if not participant:
            return []
        if str(participant) not in PARTICIPANTS_TO_MONITOR:
            return []

        self.max_values.setdefault(participant, {})
        participant_max_vals = self.max_values[participant]
        _logger.info(f'[{participant}] Tyres pressions : {telemetry.tyres_pressure}')

        car_status = session.get_car_status(participant)
        if not car_status:
            return

        participant_max_vals.setdefault(car_status.visual_tyre_compound.value, {
            'RL': 0, 'RR': 0, 'FL': 0, 'FR': 0,
        })
        max_vals = participant_max_vals[car_status.visual_tyre_compound.value]

        telemetry_key = 'tyres_inner_temperature'
        if telemetry_key not in changes:
            return []

        changed = False
        for key, value in zip(max_vals.keys(), changes[telemetry_key]):
            if value > max_vals[key]:
                max_vals[key] = value
                changed = True

        if not changed:
            return []

        return Message(
            f"{self.driver(participant)} nouvelle temp maximale atteinte : `{max_vals}`",
            Channel.SETUP
        )
