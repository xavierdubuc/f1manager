from typing import Dict, List

from src.telemetry.event import Event
from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Message
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session

from .abstract_listener import AbstractListener


class TelemetryPublicListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.PARTICIPANT_CREATED,
        Event.PARTICIPANT_LIST_INITIALIZED,
        Event.PARTICIPANT_UPDATED,
    ]

    notified = {}

    def _on_participant_list_initialized(self, session: Session, participants: List[Participant]) -> List[Message]:
        messages = []
        for participant in participants:
            if message := self._check_participant(participant):
                messages.append(message)
        return messages

    def _on_participant_created(self, session: Session, participant: Participant) -> List[Message]:
        return self._check_participant(participant)

    def _on_participant_updated(self, session: Session, changes: Dict[str, Change], participant: Participant) -> List[Message]:
        if 'telemetry_is_public' not in changes:
            return []
        return self._check_participant(participant)

    def _check_participant(self, participant: Participant) -> Message:
        if participant.name in self.notified:
            return None
        if participant.telemetry_is_public:
            return None
        self.notified[participant.name] = True
        content = f"{participant} n'a pas activé la télémétrie publique !"
        return Message(content=content)
