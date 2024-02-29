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

FIELDS_LABELS = {
    'front_wing': 'Aéro avant',
    'rear_wing': 'Aéro arrière',
    'differential_on_throttle': "Différentiel à l'accélération",
    'differential_off_throttle': "Différentiel à l'décélération",
    'front_camber': 'Carrossage avant',
    'rear_camber': 'Carrossage arrière',
    'front_toe': 'Ouverture avant',
    'rear_toe': 'Pincement arrière',
    'front_suspension': 'Suspension avant',
    'rear_suspension': 'Suspension arrière',
    'front_anti_roll_bar': 'Antiroulis avant',
    'rear_anti_roll_bar': 'Antiroulis arrière',
    'front_suspension_height': 'Garde au sol avant',
    'rear_suspension_height': 'Garde au sol arrière',
    'brake_pressure': 'Pression des freins',
    'brake_bias': 'Equilibrage des freins',
    'front_right_tyre_pressure': 'Pression avant droit',
    'front_left_tyre_pressure': 'Pression avant gauche',
    'rear_right_tyre_pressure': 'Pression arrière droit',
    'rear_left_tyre_pressure': 'Pression arrière gauche',
    'ballast': 'Lest (?)',
    'fuel_load': 'Essence'
}

class AllSetupsListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.CAR_SETUP_LIST_INITIALIZED,
        Event.CAR_SETUP_CREATED,
        Event.CAR_SETUP_UPDATED
    ]
    def __init__(self) -> None:
        super().__init__()
        self.ai_setup_notified = False

    def _on_car_setup_updated(self, car_setup:CarSetup, changes:Dict[str, Change], participant:Participant, session:Session) -> List[Message]:
        # don't mention anything about not running pilots
        if session.get_participant_status(participant) not in (ResultStatus.active, ResultStatus.invalid, ResultStatus.inactive):
            return []
        
        parts = [
            f'## {participant} a changé son setup',
            '```',
        ]

        for field, change in changes.items():
            field_str = FIELDS_LABELS[field]
            old = round(change.old, 2) if isinstance(change.old, float) else change.old
            actual = round(change.actual, 2) if isinstance(change.actual, float) else change.actual

            parts.append(f'{field_str}: {old} → {actual}')

        msg = '\n'.join(parts + ['```'])
        return [Message(content=msg, channel=Channel.SETUP)]

    def _on_car_setup_created(self, car_setup:CarSetup, session: Session, participant: Participant) -> List[Message]:
        if car_setup.has_values() and (not participant.ai_controlled or not self.ai_setup_notified):
            self.ai_setup_notified = True
            return [Message(
                content=self._setup_to_message_content(participant, car_setup),
                channel=Channel.SETUP
            )]

    def _on_car_setup_list_initialized(self, session: Session, setups: List[CarSetup]) -> List[Message]:
        messages = []
        for i, car_setup in enumerate(setups):
            if car_setup.has_values() and (not session.participants[i].ai_controlled or not self.ai_setup_notified):
                self.ai_setup_notified = True
                messages.append(Message(
                    content=self._setup_to_message_content(session.participants[i], car_setup),
                    channel=Channel.SETUP
                ))
        return messages

    def _setup_to_message_content(self, participant: Participant, car_setup: CarSetup) -> Message:
        parts = [
            f'# Setup de : {participant}',
            '```',
            str(car_setup),
            '```',
        ]
        return '\n'.join(parts)
