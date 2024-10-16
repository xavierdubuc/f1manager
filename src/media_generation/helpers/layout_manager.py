import logging
from functools import cache
from typing import Union

from src.media_generation.layout.layout import Layout
from src.media_generation.xml_parser import XMLParser

_logger = logging.getLogger(__name__)


@cache
class LayoutManager:
    def load(self, layout: Union[str, Layout]) -> Layout:
        if isinstance(layout, str):
            return self.from_xml(layout)
        return layout

    def from_xml(self, filepath: str) -> Layout:
        if not isinstance(filepath, str):
            raise TypeError(f'{filepath} is not a valid XML file path')
        _logger.info(f"Parsing layout from \"{filepath}\"")
        layout = XMLParser().parse(filepath)
        _logger.debug(layout.tree())
        return layout
