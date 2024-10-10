from dataclasses import dataclass
from typing import Any, Dict, Tuple

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.models.pilot import Pilot
from src.media_generation.readers.race_reader_models.race_ranking import RaceRankingRow


@dataclass
class FullSizeRankingRowLayout(Layout):
    fastest_lap_bg: Tuple[int, int, int, int] = ()
    driver_of_the_day_bg: Tuple[int, int, int, int] = ()
    default_bg: Tuple[int, int, int, int] = ()
    bg_transparency: int = 50

    def _paste_child(self, img: PngImageFile, key: str, child: Layout, context: Dict[str, Any] = dict):
        race_ranking_row: RaceRankingRow = context.get('race_ranking_row')
        pilot: Pilot = race_ranking_row.pilot
        if pilot and pilot.team and key == "bg":
            child.bg = pilot.team.standing_bg+(self.bg_transparency,)
        return super()._paste_child(img, key, child, context)

    def _get_children_context(self, context: Dict[str, Any] = ...) -> Dict[str, Any]:
        ctx = super()._get_children_context(context)
        race_ranking_row: RaceRankingRow = context.get('race_ranking_row')
        if not race_ranking_row:
            return ctx

        if race_ranking_row.pilot:
            pilot: Pilot = race_ranking_row.pilot
            if pilot:
                ctx['team_logo_path'] = pilot.team.get_results_logo_path()

        ctx['bg_color_2'] = None
        if race_ranking_row.is_driver_of_the_day and race_ranking_row.has_fastest_lap:
            ctx['bg_color'] = self.driver_of_the_day_bg
            ctx['bg_color_2'] = self.fastest_lap_bg

        elif race_ranking_row.is_driver_of_the_day:
            ctx['bg_color'] = self.driver_of_the_day_bg
        elif race_ranking_row.has_fastest_lap:
            ctx['bg_color'] = self.fastest_lap_bg
        else:
            ctx['bg_color'] = self.default_bg
        return ctx
