import logging
from typing import Dict, List
from src.telemetry.event import Event

from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Channel, Message

from src.telemetry.models.enums.pit_status import PitStatus
from src.telemetry.models.lap import Lap
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)


class PitListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.LAP_UPDATED
    ]

    notified = {}

    def _on_lap_updated(self, lap: Lap, changes: Dict[str, Change], participant: Participant, session: Session) -> List[Message]:
        if 'pit_status' in changes:
            pit_status = changes['pit_status'].actual
            if pit_status == PitStatus.pitting:
                if lap.result_status.is_still_in_the_race():

                    msg = f'⤴️ **{participant}** rentre au stand...'
                    return [Message(msg, Channel.PIT)]
            if pit_status == PitStatus.not_in_pit:
                car_status = session.get_car_status(participant)
                if not car_status:
                    return
                tyres_str = f'{car_status.visual_tyre_compound.get_long_string()} ({car_status.tyres_age_laps} tours)'
                fuel = round(car_status.fuel_remaining_laps, 2)
                stop_time = changes['pit_stop_timer_in_ms'].old if 'pit_stop_timer_in_ms' in changes else None
                lane_time = changes['pit_lane_time_in_lane_in_ms'].old if 'pit_lane_time_in_lane_in_ms' in changes else None

                t = f'({round(stop_time/1000,2)}s)' if stop_time else ''
                tt = f' (Total: {round(lane_time/1000,2)}s)' if lane_time else ''
                msg = f'🟢 **{participant}** sort des stands avec des pneus {tyres_str} et {fuel} tours d\'essence {t}{tt}'
                return [Message(msg, Channel.PIT)]
