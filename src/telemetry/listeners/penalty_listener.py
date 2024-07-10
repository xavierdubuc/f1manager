import logging
from typing import Dict, List

from src.telemetry.event import Event
from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Channel, Message
from src.telemetry.models.lap import Lap
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from tabulate import tabulate

from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)

TABLE_FORMAT = "simple_outline"


class PenaltyListener(AbstractListener):
    SUBSCRIBED_EVENTS = [Event.LAP_UPDATED, Event.SESSION_ENDED]

    def _get_id(self, session: Session) -> str:
        return f'{session.session_identifier}_{session.session_type.name}_penalties'

    def _on_session_ended(self, session: Session) -> List[Message]:
        table_message = self._get_table_message(session)
        if table_message:
            return [Message(table_message, Channel.PENALTY, id=self._get_id())]
        return None

    def _on_lap_updated(self, lap: Lap, changes: Dict[str, Change], participant: Participant, session: Session) -> List[Message]:
        if "corner_cutting_warnings" not in changes and "penalties" not in changes:
            return

        elements = []
        if table_message_content := self._get_table_message(session):
            elements.append(table_message_content)
        if last_update_message_content := self._get_last_update_message(changes, participant, session):
            elements.append(last_update_message_content)

        return [Message("\n".join(elements), Channel.PENALTY, id=self._get_id())]

    def _get_last_update_message(self, changes: Dict[str, Change], participant: Participant, session: Session) -> Message:
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

    def _get_table_message(self, session: Session) -> Message:
        table_values = []
        for p in session.participants:
            lap = session.get_current_lap(p)
            if lap.corner_cutting_warnings == lap.total_warnings == lap.penalties == 0:
                continue
            table_values.append(
                (str(p), lap.corner_cutting_warnings, lap.total_warnings, lap.penalties)
            )
        if len(table_values) == 0:
            return
        values = sorted(table_values, key=lambda x: (x[3], x[2], x[1]), reverse=True)
        _logger.info("Penalty ranking:")
        values_str = tabulate(values, tablefmt=TABLE_FORMAT, headers=('', 'Virages', 'Avert.', 'Péna (s)'))
        _logger.info(values_str)
        return Message(content=f"```{values_str}```", channel=Channel.PENALTY)
