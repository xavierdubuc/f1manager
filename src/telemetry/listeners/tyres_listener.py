import logging
from typing import Dict, List
from src.telemetry.event import Event

from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Channel, Message

from src.telemetry.models.damage import Damage
from src.telemetry.models.lap import Lap
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from .abstract_table_and_message_listener import AbstractTableAndMessageListener


_logger = logging.getLogger(__name__)
TABLE_FORMAT = "plain"


class TyresListener(AbstractTableAndMessageListener):
    SUBSCRIBED_EVENTS = [
        Event.LAP_CREATED
    ]

    def _on_lap_created(self, lap: Lap, participant: Participant, session: Session) -> List[Message]:
        return self._get_fixed_message(lap, participant, session)

    def _get_fixed_message_id(self, lap: Lap, participant: Participant, session: Session, *args, **kwargs) -> str:
        return f'{session.session_identifier}_{session.session_type.name}_tyres'

    def _get_fixed_message_channel(self, lap: Lap, participant: Participant, session: Session, *args, **kwargs) -> str:
        return Channel.CLASSIFICATION

    def _get_table(self, lap: Lap, participant: Participant, session: Session, *args, **kwargs) -> str:
        driver_size = max(len(str(p.name_str)) for p in session.participants) + 1
        participants = sorted(session.participants, key=lambda participant: session.get_current_lap(participant).car_position)
        table_values = [
            f"`{' '*driver_size}          AvG AvD ArG ArD`",
        ] + [self._get_table_line(p, session, driver_size) for p in participants]
        table_str = "\n".join(table_values)
        return f'## Pneus\n{table_str}'

    def _get_update_message(self, lap: Lap, participant: Participant, session: Session, *args, **kwargs) -> str:
        return f"Dernière mise à jour : tour {lap.current_lap_num}"

    def _get_table_line(self, participant: Participant, session: Session, driver_size: int = 16) -> str:
        #` 6`:ferrari:`LECLERC   `:soft:` 0% 0% 1% 0%`
        elements = []
        if lap := session.get_current_lap(participant):
            # POSITION
            elements.append(f'`{str(lap.car_position).rjust(2)}` ')
        # TEAMOJI
        if teamoji := self.get_teamoji(participant):
            elements.append(teamoji)
        # DRIVER NAME
        elements.append(f'`{str(participant).ljust(driver_size)}`')
        # TYRE
        if car_status := session.get_car_status(participant):
            elements.append(self.tyre(car_status.visual_tyre_compound))
        # TYRE DAMAGES
        if damage := session.get_car_damage(participant):
            elements += [
                "` ",
                f"{str(damage.get_front_left_tyre_damage_value()).rjust(2)}% ",
                f"{str(damage.get_front_right_tyre_damage_value()).rjust(2)}% ",
                f"{str(damage.get_rear_left_tyre_damage_value()).rjust(2)}% ",
                f"{str(damage.get_rear_right_tyre_damage_value()).rjust(2)}% ",
                "`",
            ]
        # ERS
        if car_status:
            ersmoji = '🔋' if car_status.ers_left >= 50 else '🪫'
            elements.append(f'{ersmoji}`{str(car_status.ers_left).rjust(3)}%`')
        return "".join(elements)
