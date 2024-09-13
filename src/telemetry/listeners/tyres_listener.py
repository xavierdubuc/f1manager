import logging
from typing import Dict, List
from src.telemetry.event import Event

from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Channel, Message

from src.telemetry.models.damage import Damage
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from .abstract_table_and_message_listener import AbstractTableAndMessageListener


_logger = logging.getLogger(__name__)
TABLE_FORMAT = "plain"


class TyresListener(AbstractTableAndMessageListener):
    SUBSCRIBED_EVENTS = [
        Event.DAMAGE_UPDATED
    ]

    def _get_fixed_message_id(self, damage: Damage, changes: Dict[str, Change], participant: Participant, session: Session, *args, **kwargs) -> str:
        return f'{session.session_identifier}_{session.session_type.name}_tyres'

    def _get_fixed_message_channel(self, damage: Damage, changes: Dict[str, Change], participant: Participant, session: Session, *args, **kwargs) -> Channel:
        return Channel.CLASSIFICATION

    def _on_damage_updated(self, damage: Damage, changes: Dict[str, Change], participant: Participant, session: Session) -> List[Message]:
        if 'tyres_damage' not in changes:
            return
        return self._get_fixed_message(damage, changes, participant, session)

    def _get_update_message(self, *args, **kwargs) -> str:
        return super()._get_update_message(*args, **kwargs)

    def _get_table(self, damage: Damage, changes: Dict[str, Change], participant: Participant, session: Session, *args, **kwargs) -> str:
        driver_size = max(len(str(p.name_str)) for p in session.participants)
        table_values = [
            f"`{' '*driver_size}      AvG AvD ArG ArD`",
        ] + [self._get_table_line(p, session, driver_size) for p in session.participants]
        table_str = "\n".join(table_values)
        return f'## Pneus\n```{table_str}```'

    def _get_update_message(self, damage: Damage, changes: Dict[str, Change], participant: Participant, session: Session, *args, **kwargs) -> str:
        old_tyres_wear = max(changes.get('tyres_damage').old)
        actual_tyres_wear = max(changes.get('tyres_damage').actual)
        car_status = session.get_car_status(participant)
        tyre = self.tyre(car_status.visual_tyre_compound)
        if actual_tyres_wear == 100:
            return
        if actual_tyres_wear > 60:
            return f'{tyre} **{self.driver(participant, session)}** a des pneus très usés !'
        elif actual_tyres_wear > old_tyres_wear:
            return f'{tyre} **{self.driver(participant, session)}** use ses pneus !'
        elif actual_tyres_wear < old_tyres_wear:
            return f'{tyre} **{self.driver(participant, session)}** a changé de pneu !'

    def _get_table_line(self, participant: Participant, session: Session, driver_size: int = 16) -> str:
        elements = []
        # POSITION
        if lap := session.get_current_lap(participant):
            elements.append(f'`{str(lap.car_position).rjust(2)}`')
        # TEAMOJI
        if teamoji := self.get_teamoji(participant):
            elements.append(teamoji)
        # DRIVER NAME
        elements.append(str(participant).ljust(driver_size))
        # TYRE
        car_status = session.get_car_status(participant)
        elements.append(self.tyre(car_status.visual_tyre_compound))
        # TYRE DAMAGES
        damage = session.get_car_damage(participant)
        elements += [
            f"{str(damage.get_front_left_tyre_damage_value()).rjust(2)}%",
            f"{str(damage.get_front_right_tyre_damage_value()).rjust(2)}%",
            f"{str(damage.get_rear_left_tyre_damage_value()).rjust(2)}%",
            f"{str(damage.get_rear_right_tyre_damage_value()).rjust(2)}%",
        ]
        return "".join(elements)
