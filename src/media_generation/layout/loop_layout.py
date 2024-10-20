from dataclasses import dataclass
from typing import Any, Dict

import logging
from src.media_generation.layout.layout import Layout


_logger = logging.getLogger(__name__)


@dataclass
class LoopLayout(Layout):
    iterable: str = None
    iterator: str = None

    def _get_template_instance_context(self, i: int, context: Dict[str, Any] = {}):
        ctx = super()._get_template_instance_context(i, context)
        if not self.iterable or not self.iterator:
            _logger.error(f'Iterator or iterable is not set on {self.name}')
            return ctx
        iterable = context.get(self.iterable, [])
        if not iterable:
            _logger.debug(f'Iterable is falsy ({iterable})')
            return ctx
        if 0 <= i < len(iterable):
            _logger.debug(f'Adding {self.iterator} variable as {i}th value of {self.iterable} for {self}')
            return {
                self.iterator: iterable[i],
                "even": i % 2 == 0,
                "i": i,
            }
        _logger.error(f'{i} is out of range of {len(iterable)} for {self}')
        return None
