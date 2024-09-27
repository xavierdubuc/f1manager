from dataclasses import dataclass
from typing import Any, Dict, Tuple

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.models.pilot import Pilot
from src.media_generation.readers.race_reader_models.race_ranking import RaceRankingRow


@dataclass
class SimpleRankingRowLayout(Layout):
    fastest_lap_bg: Tuple[int, int, int, int] = ()
    nt_bg: Tuple[int, int, int, int] = ()
    driver_of_the_day_bg: Tuple[int, int, int, int] = ()
    even_bg: Tuple[int, int, int, int] = ()
    odd_bg: Tuple[int, int, int, int] = ()

    def _get_children_context(self, context: Dict[str, Any] = ...) -> Dict[str, Any]:
        ctx = super()._get_children_context(context)
        race_ranking_row: RaceRankingRow = context.get('race_ranking_row')
        if not race_ranking_row:
            return ctx

        default_bg = self.odd_bg if race_ranking_row.position % 2 == 1 else self.even_bg

        ctx['bg_color_2'] = None
        if race_ranking_row.split in ('NT', 'DSQ'):
            ctx['bg_color'] = self.nt_bg
        else:
            if race_ranking_row.is_driver_of_the_day and race_ranking_row.has_fastest_lap:
                ctx['bg_color'] = self.driver_of_the_day_bg
                ctx['bg_color_2'] = self.fastest_lap_bg

            elif race_ranking_row.is_driver_of_the_day:
                ctx['bg_color'] = self.driver_of_the_day_bg
            elif race_ranking_row.has_fastest_lap:
                ctx['bg_color'] = self.fastest_lap_bg
            else:
                ctx['bg_color'] = default_bg

        if race_ranking_row.pilot:
            pilot: Pilot = race_ranking_row.pilot
            if pilot:
                ctx['team_logo_path'] = pilot.team.get_results_logo_path()
                ctx['team_name'] = pilot.team.title.upper()
        return ctx
