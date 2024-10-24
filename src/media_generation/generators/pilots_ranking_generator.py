from dataclasses import dataclass

from src.media_generation.readers.general_ranking_models.pilot_ranking import (
    PilotRanking, PilotRankingRow)

from ..generators.abstract_generator import AbstractGenerator



@dataclass
class PilotsRankingGenerator(AbstractGenerator):
    visual_type: str = 'pilots_ranking'

    def _get_layout_context(self):
        ctx = super()._get_layout_context()
        ranking = []
        previous_pilot_points = None
        previous_ranking = self.config.ranking.get_previous_ranking()
        for i, row in enumerate(self.config.ranking):
            # SHOW ROW OR NOT (ex: if identifier is "main" and pilot is reservist)
            if not self._pilot_should_be_shown(row):
                continue

            is_champion = False  # i == 0 # FIXME
            # DETERMINE POSITION
            points = row.total_points
            if previous_pilot_points is not None and previous_pilot_points == points:
                position = '-'
            else:
                position = str(i+1)

            # DETERMINE DELTA
            if not previous_ranking:
                progression = 0
            else:
                previous_pos, previous_ranking_row = previous_ranking.find(row.pilot)
                progression = (previous_pos - (i+1)) if previous_pos is not None else None

            # GENERATE AND PASTE IMAGE
            ranking.append({
                "is_champion": is_champion,
                "position_str": position,
                "progression": progression,
                "row": row,
                "is_last": False,
            })

            # UPDATE LOOP VARIABLES
            previous_pilot_points = row.total_points
        ranking[-1]["is_last"] = True
        ctx["ranking"] = ranking
        return ctx

    def _pilot_should_be_shown(self, row: PilotRankingRow) -> bool:
        if self.identifier == 'main':
            return not row.pilot.reservist
        if self.identifier == 'reservists':
            return row.pilot.reservist
        return True
