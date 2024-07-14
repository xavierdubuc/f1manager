import logging
from typing import List

from src.telemetry.event import Event
from src.telemetry.message import Channel, Message
from src.telemetry.models.session import Session
from src.telemetry.models.speed_trap_entry import SpeedTrapEntry
from tabulate import tabulate

from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)

TABLE_FORMAT = "plain"


class SpeedTrapListener(AbstractListener):
    SUBSCRIBED_EVENTS = [Event.SPEED_TRAP, Event.SESSION_ENDED]

    def _on_session_ended(self, session: Session) -> List[Message]:
        if table_message := self._get_table_message(session):
            return [table_message]
        return None

    def _on_speed_trap(self, speed_trap:SpeedTrapEntry, session: Session) -> List[Message]:
        key = speed_trap.participant
        existing_speedtrap = session.speed_traps.get(key)
        if existing_speedtrap and existing_speedtrap >= speed_trap:
            return []

        session.speed_traps[key] = speed_trap
        messages = [self._get_last_update_message(speed_trap, session)]
        if table_message := self._get_table_message(session):
            messages.append(table_message)
        return messages

    def _get_last_update_message(self, speed_trap: SpeedTrapEntry, session: Session) -> Message:
        id = f'{session.session_identifier}_{session.session_type.name}_last_speedtrap_update'
        msg = f'**SPEED TRAP 🚀** `{self.driver(speed_trap.participant)} {round(speed_trap.participant_speed)} km/h !`'
        return Message(content=msg, channel=Channel.CLASSIFICATION, local_id=id)

    def _get_table_message(self, session: Session) -> Message:
        id = f'{session.session_identifier}_{session.session_type.name}_speed_traps'
        table_values = [
            (str(participant), speed_trap.participant_speed)
            for participant, speed_trap in session.speed_traps.items()
        ]
        if len(table_values) == 0:
            return
        values = sorted(table_values, key=lambda x: x[1], reverse=True)
        values = [(i+1, v[0], f'{round(v[1])} km/h') for i,v in enumerate(values)]
        values_str = tabulate(values, tablefmt=TABLE_FORMAT)
        return Message(content=f"## Speed trap ranking\n```{values_str}```", channel=Channel.CLASSIFICATION, local_id=id)
