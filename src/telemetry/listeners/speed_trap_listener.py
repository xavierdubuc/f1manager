import logging
from typing import List

from src.telemetry.event import Event
from src.telemetry.message import Channel, Message
from src.telemetry.models.session import Session
from src.telemetry.models.speed_trap_entry import SpeedTrapEntry
from tabulate import tabulate

from .abstract_table_and_message_listener import AbstractTableAndMessageListener

_logger = logging.getLogger(__name__)

TABLE_FORMAT = "plain"


class SpeedTrapListener(AbstractTableAndMessageListener):
    SUBSCRIBED_EVENTS = [Event.SPEED_TRAP, Event.CLASSIFICATION_LIST_INITIALIZED]

    def _on_classification_list_initialized(self, session: Session, *args, **kwargs) -> List[Message]:
        return self._get_fixed_message(session)

    def _on_speed_trap(self, speed_trap: SpeedTrapEntry, session: Session) -> List[Message]:
        key = speed_trap.participant
        existing_speedtrap = session.speed_traps.get(key)
        if existing_speedtrap and existing_speedtrap >= speed_trap:
            if not existing_speedtrap.participant.has_name and speed_trap.participant.has_name:
                existing_speedtrap.participant = speed_trap.participant
            if not existing_speedtrap.fastest_participant.has_name and speed_trap.fastest_participant.has_name:
                existing_speedtrap.fastest_participant = speed_trap.fastest_participant
            return

        session.speed_traps[key] = speed_trap
        return self._get_fixed_message(session, speed_trap)

    def _get_fixed_message_id(self, session: Session, *args, **kwargs) -> str:
        return f'{session.session_identifier}_{session.session_type.name}_speed_traps'

    def _get_fixed_message_channel(self, event: Event, *args, **kwargs) -> Channel:
        return Channel.CLASSIFICATION

    def _get_update_message(self, session: Session, speed_trap: SpeedTrapEntry = None, *args, **kwargs) -> Message:
        if not speed_trap:
            return
        return f'🚀 **{self.driver(speed_trap.participant, session)}** {round(speed_trap.participant_speed)} km/h !'

    def _get_table(self, session: Session, *args, **kwargs) -> Message:
        table_values = [
            (str(participant), speed_trap.participant_speed)
            for participant, speed_trap in session.speed_traps.items()
        ]
        if len(table_values) == 0:
            return
        values = sorted(table_values, key=lambda x: x[1], reverse=True)
        values = [(i+1, v[0], f'{round(v[1])} km/h') for i, v in enumerate(values)]
        values_str = tabulate(values, tablefmt=TABLE_FORMAT)
        return f"## Speed trap ranking\n```{values_str}```"
