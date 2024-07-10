import logging
from typing import List, Tuple

from src.telemetry.event import Event
from src.telemetry.message import Channel, Message
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session

from src.telemetry.models.tyreset import TyreSet

from .abstract_listener import AbstractListener


class TyreSetListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.TYRESET_LIST_CREATED,
        Event.TYRESET_LIST_UPDATED,
    ]

    def _on_tyreset_list_created(self, tyresets: List[TyreSet], participant: Participant, session: Session):
        table_message = self._get_driver_message(tyresets, participant, session)
        return [table_message]

    def _on_tyreset_list_updated(self, tyresets: List[TyreSet], participant: Participant, session: Session):
        table_message = self._get_driver_message(tyresets, participant, session)
        return [table_message]

    def _get_driver_message(self, tyresets: List[TyreSet], participant: Participant, session: Session) -> Message:
        elements = []
        fitted_tyreset: TyreSet = None
        wet_tyresets: List[Tuple[int, TyreSet]] = []
        dry_tyresets: List[Tuple[int, TyreSet]] = []
        for i, tyreset in enumerate(tyresets):
            if not tyreset.available:
                continue
            tyreset_with_id = (i, tyreset)
            if tyreset.fitted:
                fitted_tyreset = tyreset_with_id
            else:
                if tyreset.visual_tyre_compound.is_wet():
                    wet_tyresets.append(tyreset_with_id)
                else:
                    dry_tyresets.append(tyreset_with_id)

        if fitted_tyreset:
            elements.append(
                f'{self.driver(participant, session)} [{self.tyreset_with_id(fitted_tyreset)}]'
            )

        if len(dry_tyresets) != 0:
            elements.append(" - ".join(self.tyreset_with_id(tyreset) for tyreset in dry_tyresets))

        if len(wet_tyresets) != 0:
            elements.append(" - ".join(self.tyreset_with_id(tyreset) for tyreset in wet_tyresets))

        if len(elements) == 0:
            return

        id = f"{session.session_identifier}_tyreset_{session.session_type.name}_{participant.race_number}"
        return Message(
            content='\n> '.join(elements),
            channel=Channel.PIT,
            local_id=id
        )

    def tyreset_with_id(self, tyreset: Tuple[int, TyreSet]):
        tyre = self.tyre(tyreset[1].visual_tyre_compound, tyreset[1].wear)
        return f'#{tyreset[0]} {tyre}'
