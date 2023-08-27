import logging
from typing import Dict, List
from src.telemetry.event import Event

from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Channel, Message

from src.telemetry.models.damage import Damage
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)


class TyresOldListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.DAMAGE_UPDATED
    ]

    notified = {}

    def _on_damage_updated(self, damage: Damage, changes: Dict[str, Change], participant: Participant, session: Session) -> List[Message]:
        if 'tyres_damage' in changes:
            tyres_wear = changes.get('tyres_damage').actual
            if participant.name[-3:] == 'REZ':
                print(damage)
                print(tyres_wear)
                print(self.notified)
            if self.notified.get(participant.name, False): # if he's already notified
                if all(t < 70 for t in tyres_wear):
                    self.notified[participant.name] = False
            else:
                if any(t > 70 for t in tyres_wear):
                    self.notified[participant.name] = True
                    tyres_wear_str = ','.join(f'{str(t).rjust(3)}%' for t in tyres_wear)
                    msg = f"Les pneus de **{participant}** sont très usés `{tyres_wear_str}` !"
                    return [Message(content=msg, channel=Channel.DAMAGE)]
        return []
