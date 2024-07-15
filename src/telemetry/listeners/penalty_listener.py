import logging
from typing import Dict, List

from src.telemetry.event import Event
from src.telemetry.listeners.abstract_fixed_message_listener import AbstractFixedMessageListener
from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Channel, Message
from src.telemetry.models.lap import Lap
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from tabulate import tabulate

from .abstract_table_and_message_listener import AbstractTableAndMessageListener

_logger = logging.getLogger(__name__)

TABLE_FORMAT = "simple_outline"


class PenaltyListener(AbstractTableAndMessageListener):
    SUBSCRIBED_EVENTS = [Event.LAP_UPDATED, Event.SESSION_ENDED]

    def _on_session_ended(self, session: Session) -> List[Message]:
        return self._get_fixed_message(session)

    def _on_lap_updated(self, lap: Lap, changes: Dict[str, Change], participant: Participant, session: Session) -> List[Message]:
        if "corner_cutting_warnings" not in changes and "penalties" not in changes:
            return

        return self._get_fixed_message(session, changes)

    def _get_fixed_message_id(self, session: Session, *args, **kwargs) -> str:
        return f'{session.session_identifier}_{session.session_type.name}_penalties'

    def _get_fixed_message_channel(self, event: Event, *args, **kwargs) -> Channel:
        return Channel.PENALTY

    def _get_update_message(self, session: Session, lap: Lap, changes: Dict[str, Change] = None, participant: Participant = None, *args, **kwargs) -> str:
        if not changes or not participant:
            return

        if "penalties" in changes:
            seconds_of_penalties = changes["penalties"].actual
            seconds_of_penalties_before = changes["penalties"].old
            diff = seconds_of_penalties - seconds_of_penalties_before
            if diff > 0:
                flagmoji = self.get_emoji("blackwhiteflag", "🏴")
                return f"{flagmoji} **{self.driver(participant)}** a recu une pénalité de {diff} secondes !"
            diff = -diff
            return f"✅ **{self.driver(participant)}** a purgé une pénalité de {diff} secondes !"

        if "corner_cutting_warnings" in changes:
            amount_of_warnings = changes["corner_cutting_warnings"].actual
            return f"🏳️ **{self.driver(participant)}** a recu un avertissement ! **Total : {amount_of_warnings}**"

    def _get_table(self, session: Session, *args, **kwargs) -> str:
        table_values = []
        for p in session.participants:
            lap = session.get_current_lap(p)
            table_values.append(
                (str(p), lap.corner_cutting_warnings, lap.total_warnings, lap.penalties)
            )
        if len(table_values) == 0:
            return
        values = sorted(table_values, key=lambda x: (x[3], x[2], x[1]), reverse=True)
        _logger.info("Penalty ranking:")
        values_str = tabulate(values, tablefmt=TABLE_FORMAT, headers=('', 'Virages', 'Avert.', 'Péna (s)'))
        _logger.info(values_str)
        return f"```{values_str}```"
