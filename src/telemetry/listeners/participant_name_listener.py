from typing import Dict, List

from src.telemetry.event import Event
from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Message
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session

from .abstract_listener import AbstractListener


class ParticipantNameListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.PARTICIPANT_CREATED,
        Event.PARTICIPANT_LIST_INITIALIZED,
        Event.PARTICIPANT_UPDATED,
    ]

    def _on_participant_list_initialized(self, session: Session, participants: List[Participant]) -> List[Message]:
        for participant in participants:
            self._ensure_participant_has_name(participant, session)
        return []

    def _on_participant_created(self, session: Session, participant: Participant) -> List[Message]:
        self._ensure_participant_has_name(participant, session)
        return []

    def _on_participant_updated(self, participant: Participant, changes: Dict[str, Change], session: Session) -> List[Message]:
        if 'name' in changes:
            self._ensure_participant_has_name(participant, session)
        return []

    def _ensure_participant_has_name(self, participant: Participant, session: Session) -> Message:
        if participant.has_name:
            return
        if not session.config:
            return

        pilot = session.config.find_pilot(participant)
        if pilot:
            participant.name = pilot.name
