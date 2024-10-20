from dataclasses import dataclass

from ..generators.abstract_generator import AbstractGenerator
from ..helpers.transform import *


@dataclass
class TeamsRankingGenerator(AbstractGenerator):
    visual_type: str = 'teams_ranking'

    def _get_layout_context(self):
        ctx = super()._get_layout_context()
        ranking = []
        previous_pilot_points = None
        previous_ranking = self.config.ranking.get_previous_ranking()
        for i, row in enumerate(self.config.ranking):
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
                previous_pos, previous_ranking_row = previous_ranking.find(row.team)
                progression = (previous_pos - (i+1)) if previous_pos is not None else None

            ranking.append({
                "is_champion": is_champion,
                "position_str": position,
                "progression": progression,
                "row": row,
            })

            # UPDATE LOOP VARIABLES
            previous_pilot_points = row.total_points

        ctx["ranking"] = ranking
        return ctx
