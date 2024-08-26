from dataclasses import dataclass
from typing import Any, Dict

from src.media_generation.layout.layout import Layout
from src.media_generation.readers.race_reader_models.race import Race
from src.media_generation.readers.race_reader_models.race_ranking import RaceRanking


@dataclass
class RaceRankingLayout(Layout):
    race_ranking: RaceRanking = None
    initial_position: int = 1

    def _get_race_ranking(self, context: Dict[str, Any] = {}):
        if not self.race_ranking:
            race: Race = context.get('race')
            if race:
                self.race_ranking = race.race_result
        return self.race_ranking

    def _get_template_instance_context(self, i: int, context: Dict[str, Any] = {}):
        race_ranking = self._get_race_ranking(context)
        if not race_ranking:
            return super()._get_template_instance_context(i, context)
        index = (self.initial_position-1) + i
        race_ranking_row = race_ranking.rows[index] if 0 <= index < len(race_ranking.rows) else None
        return {
            'race_ranking_row': race_ranking_row,
            'pilot_name': race_ranking_row.pilot_name.upper() if race_ranking_row and race_ranking_row.pilot_name else '',
            'pilot': race_ranking_row.pilot if race_ranking_row and race_ranking_row.pilot else None
        }
