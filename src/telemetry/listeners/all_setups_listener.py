from typing import Dict, List
from src.telemetry.event import Event

from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Channel, Message
from src.telemetry.models.car_setup import CarSetup
from src.telemetry.models.damage import Damage
from src.telemetry.models.enums.result_status import ResultStatus
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from .abstract_listener import AbstractListener

class AllSetupsListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.CAR_SETUP_CREATED,
        Event.CAR_SETUP_UPDATED
    ]

    def _on_car_setup_updated(self, car_setup:CarSetup, changes:Dict[str, Change], participant:Participant, session:Session) -> List[Message]:
        # don't mention anything about not running pilots
        if session.get_participant_status(participant) not in (ResultStatus.active, ResultStatus.invalid, ResultStatus.inactive):
            return []
        
        parts = [
            f'## {participant} a changé son setup',
            '```',
        ]

        for field, change in changes:
            parts.append(f'{field}: {change.old} → {change.actual}')

        msg = '\n'.join(parts + ['```'])
        return [Message(content=msg, channel=Channel.SETUP)]

    def _on_car_setup_created(self, car_setup:CarSetup, session: Session, participant: Participant) -> List[Message]:
        parts = [
            f'# Setup de : {participant}',
            '```',
            str(car_setup),
            '```',
        ]
        msg = '\n'.join(parts)
        return [Message(content=msg, channel=Channel.SETUP)]
        
        
