from dataclasses import dataclass
from typing import Any, Dict

from src.media_generation.layout.layout import Layout
from src.media_generation.readers.race_reader_models.race import Race
from src.media_generation.readers.race_reader_models.race_ranking import RaceRanking


@dataclass
class RaceRankingLayout(Layout):
    initial_position: int = 1

    def _get_template_instance_context(self, i: int, context: Dict[str, Any] = {}):
        race: Race = context.get('race')
        if not race:
            return None

        race_ranking = race.race_result
        if not race_ranking:
            return None

        index = (self.initial_position-1) + i
        race_ranking_row = race_ranking.rows[index] if 0 <= index < len(race_ranking.rows) else None
        if not race_ranking_row:
            return None

        return {
            'race_ranking_row': race_ranking_row,
            'pilot_name': race_ranking_row.pilot_name.upper() if race_ranking_row and race_ranking_row.pilot_name else '',
            'pilot': race_ranking_row.pilot if race_ranking_row and race_ranking_row.pilot else None,
            'is_last': index == len(race_ranking.rows) - 1
        }
