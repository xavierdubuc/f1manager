from dataclasses import dataclass
from typing import Any, Dict, Tuple

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.models.pilot import Pilot
from src.media_generation.readers.race_reader_models.race_ranking import RaceRankingRow


@dataclass
class SimpleRankingRowLayout(Layout):
    fastest_lap_bg: Tuple[int, int, int, int] = ()
    driver_of_the_day_bg: Tuple[int, int, int, int] = ()
    even_bg: Tuple[int, int, int, int] = ()
    odd_bg: Tuple[int, int, int, int] = ()

    def _get_children_context(self, context: Dict[str, Any] = ...) -> Dict[str, Any]:
        ctx = super()._get_children_context(context)
        race_ranking_row: RaceRankingRow = context.get('race_ranking_row')
        if not race_ranking_row:
            return ctx
        if race_ranking_row.is_driver_of_the_day:
            bg_color = self.driver_of_the_day_bg
        elif race_ranking_row.has_fastest_lap: # what about half/half if both ? FIXME
            bg_color = self.fastest_lap_bg
        else:
            bg_color = self.odd_bg if race_ranking_row.position % 2 == 1 else self.even_bg
        ctx['bg_color'] = bg_color
        return ctx
