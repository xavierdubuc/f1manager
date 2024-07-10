import logging
from typing import List

from src.telemetry.event import Event
from src.telemetry.message import Channel, Message
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from src.telemetry.models.speed_trap_entry import SpeedTrapEntry
from tabulate import tabulate

from src.telemetry.models.tyreset import TyreSet

from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)

TABLE_FORMAT = "simple_outline"


class TyreSetListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.TYRESET_LIST_CREATED,
        Event.TYRESET_LIST_UPDATED,
    ]

    def _on_tyreset_list_created(self, tyresets:List[TyreSet], participant:Participant, session:Session):
        table_message = self._get_table_message(tyresets, participant, session)
        return [table_message]

    def _on_tyreset_list_updated(self, tyresets:List[TyreSet], participant:Participant, session:Session):
        table_message = self._get_table_message(tyresets, participant, session)
        return [table_message]

    def _get_table_message(self, tyresets:List[TyreSet], participant:Participant, session:Session) -> Message:
        elements = [
            f'## {self.driver(participant, session)} available tyres'
        ]

        tyres_ids = [
            f'`{str(i).rjust(2)}`' for i in range(1, 21)
        ]
        tyres_emojis = [
            self.get_tyremoji(tyreset.visual_tyre_compound) for tyreset in tyresets
        ]
        tyres_wear = [
            f'{str(tyreset.wear).rjust(3)} %' for tyreset in tyresets
        ]
        is_fitted = [
            '✅' if tyreset.fitted else ' ' for tyreset in tyresets
        ]

        if len(tyres_emojis) == 0:
            return

        elements.append(' '.join(tyres_ids))
        elements.append(' '.join(tyres_emojis))
        elements.append(' '.join(tyres_wear))
        elements.append(' '.join(is_fitted))

        id = f"{session.session_identifier}_tyreset_{session.session_type.name}_{participant.race_number}"
        return Message(
            content='\n'.join(elements),
            channel=Channel.PIT,
            local_id=id
        )
