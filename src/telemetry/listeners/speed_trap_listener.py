import logging
from typing import List

from src.telemetry.event import Event
from src.telemetry.message import Channel, Message
from src.telemetry.models.session import Session
from src.telemetry.models.speed_trap_entry import SpeedTrapEntry
from tabulate import tabulate

from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)

TABLE_FORMAT = "simple_outline"


class SpeedTrapListener(AbstractListener):
    SUBSCRIBED_EVENTS = [Event.SPEED_TRAP, Event.SESSION_ENDED]

    def _on_session_ended(self, session: Session) -> List[Message]:
        table_message = self._get_table_message(session)
        return [table_message]

    def _on_speed_trap(self, speed_trap:SpeedTrapEntry, session: Session) -> List[Message]:
        key = speed_trap.participant
        existing_speedtrap = session.speed_traps.get(key)
        if existing_speedtrap and existing_speedtrap >= speed_trap:
            return []

        session.speed_traps[key] = speed_trap
        messages = [self._get_last_update_message(speed_trap, session)]
        table_message = self._get_table_message(session)
        if table_message:
            table_message.local_id = f'{session.session_identifier}_speed_traps'
            messages.append(table_message)
        return messages

    def _get_last_update_message(self, speed_trap: SpeedTrapEntry, session: Session) -> Message:
        lap = session.get_current_lap(speed_trap.participant)
        position = str(lap.car_position).rjust(2)
        teamoji = self.get_emoji(speed_trap.participant.team.as_emoji())
        msg = f'🚀 `{position}` {teamoji} {speed_trap.participant} {round(speed_trap.participant_speed)} km/h !'
        return Message(content=msg, channel=Channel.CLASSIFICATION, local_id=f'{session.session_identifier}_last_speedtrap_update')

    def _get_table_message(self, session: Session) -> Message:
        table_values = [
            (str(participant), speed_trap.participant_speed)
            for participant, speed_trap in session.speed_traps.items()
        ]
        if len(table_values) == 0:
            return
        values = sorted(table_values, key=lambda x: x[1], reverse=True)
        values = [(v[0], round(v[1])) for v in values]
        _logger.info("Speed trap:")
        values_str = tabulate(values, tablefmt=TABLE_FORMAT, headers=('', 'km/h'))
        _logger.info(values_str)
        return Message(content=f"Speed traps\n```{values_str}```", channel=Channel.CLASSIFICATION)
