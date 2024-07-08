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

    def _on_session_ended(self, session: Session) -> List[Message]:
        table_values = []
        for p in session.participants:
            lap = session.get_current_lap(p)
            table_values.append(
                (str(p), lap.corner_cutting_warnings, lap.total_warnings, lap.penalties)
            )
        values = sorted(table_values, key=lambda x: (x[3], x[2], x[1]), reverse=True)
        _logger.info("Fetched ranking that will be stored :")
        values_str = tabulate(values, tablefmt=TABLE_FORMAT)
        _logger.info(values_str)
        return [Message(content=f"```{values_str}```", channel=Channel.PENALTY)]

    def _on_lap_updated(
        self,
        lap: Lap,
        changes: Dict[str, Change],
        participant: Participant,
        session: Session,
    ) -> List[Message]:
        messages = []
        teamoji = self.get_emoji(participant.team.as_emoji())
        if "corner_cutting_warnings" in changes:
            amount_of_warnings = changes["corner_cutting_warnings"].actual
            msg = f"🏳️ {teamoji} **{participant}** a recu un avertissement ! **Total : {amount_of_warnings}**"
            messages.append(Message(content=msg, channel=Channel.PENALTY))
        if "penalties" in changes:
            seconds_of_penalties = changes["penalties"].actual
            seconds_of_penalties_before = changes["penalties"].old
            diff = seconds_of_penalties - seconds_of_penalties_before
            if diff > 0:
                flagmoji = self.get_emoji("blackwhiteflag", "🏴")
                msg = f"{flagmoji} {teamoji} **{participant}** a recu une pénalité de {diff} secondes ! **Total : {seconds_of_penalties} secondes**"
            else:
                diff = -diff
                msg = f"✅ {teamoji} **{participant}** a purgé une pénalité de {diff} secondes ! **Total : {seconds_of_penalties} secondes**"
            messages.append(Message(content=msg, channel=Channel.PENALTY))
        return messages
