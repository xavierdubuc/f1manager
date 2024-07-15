import logging
from tabulate import tabulate
from typing import Dict, List

from src.telemetry.event import Event
from src.telemetry.managers.abstract_manager import Change
from src.telemetry.message import Message, Channel
from src.telemetry.models.classification import Classification
from src.telemetry.models.session import Session

from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)

TABLE_FORMAT = 'simple_outline'

class ClassificationListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.CLASSIFICATION_LIST_INITIALIZED,
        Event.CLASSIFICATION_UPDATED,
    ]

    def _on_classification_list_initialized(self, session: Session, final_classification: Classification) -> List[Message]:
        if session.session_type.is_clm():
            return []
        end_content = f'Fin de la session "{session.session_type}" voici le classement final'
        # TODO send final penalties in channel.penalty also
        msg = Message(content=end_content, channel=Channel.CLASSIFICATION)
        return [msg] + [
            Message(content=f"```\n{m}\n```", channel=Channel.CLASSIFICATION) for m in self._classification_to_messages(session)
        ]

    def _on_classification_updated(self, session: Session, changes:Dict[str, Change])  -> List[Message]:
        if session.session_type.is_clm():
            return []
        end_content = f'Le classement de la session "{session.session_type}" a changé !? Nouvelle version ci-dessous.'
        return [Message(content=end_content, channel=Channel.CLASSIFICATION)] + [
            Message(content=f"```\n{m}\n```", channel=Channel.CLASSIFICATION) for m in self._classification_to_messages(session)
        ]

    # PRIVATE

    def _classification_to_messages(self, session: Session):
        _logger.info('Final ranking of previous session below.')
        final_ranking = session.get_formatted_final_ranking()
        if session.session_type.is_race():
            colalign = ('right', 'left', 'right', 'left', 'right')
        else:
            colalign = ('right', 'left', 'right', 'right')
        if len(session.final_classification) > 12:
            return [
                tabulate(final_ranking[:10], tablefmt=TABLE_FORMAT, colalign=colalign),
                tabulate(final_ranking[10:], tablefmt=TABLE_FORMAT, colalign=colalign)
            ]
        return [tabulate(final_ranking, tablefmt=TABLE_FORMAT, colalign=colalign)]
