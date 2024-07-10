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
    SUBSCRIBED_EVENTS = [Event.TYRESET_LIST_CREATED]

    def _on_tyreset_list_created(self, tyresets:List[TyreSet], participant:Participant, session:Session):
        table_message = self._get_table_message(tyresets, participant, session)
        return [table_message]

    def _get_table_message(self, tyresets:List[TyreSet], participant:Participant, session:Session) -> Message:
        elements = [
            f'## {self.driver(participant, session)} available tyres'
        ]
        tyres = [
            self.tyre(tyreset.visual_tyre_compound, 100-tyreset.wear, tyreset.fitted)
            for tyreset in tyresets
            if tyreset.available
        ]
        if len(tyres) == 0:
            return

        elements.append(f'```{tabulate(tyres, tablefmt=TABLE_FORMAT)}```')
        return Message(content='\n'.join(elements), channel=Channel.PIT)