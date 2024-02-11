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
        return [self._setup_to_message(participant, car_setup)]

    def _on_car_setup_list_initialized(self, session: Session, setups: List[CarSetup]) -> List[Message]:
        return [
            Message(
                content=self._setup_to_message(session.participants[i], car_setup),
                channel=Channel.SETUP
            ) for i, car_setup in enumerate(setups)
        ]

    def _setup_to_message(self, participant: Participant, car_setup: CarSetup) -> Message:
        parts = [
            f'# Setup de : {participant}',
            '```',
            str(car_setup),
            '```',
        ]
        msg = '\n'.join(parts)
        return Message(content=msg, channel=Channel.SETUP)
