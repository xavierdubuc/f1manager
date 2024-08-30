from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


from src.media_generation.layout.layout import Layout


@dataclass
class TimingRowsLayout(Layout):
    ranking: List[List[str]] = None
    odd_bg: Tuple[int, int, int, int] = (100, 100, 100, 100)
    even_bg: Tuple[int, int, int, int] = (50, 50, 50, 100)
    default_fg: Tuple[int, int, int, int] = (255, 255, 255, 255)
    fastest_fg: Tuple[int, int, int, int] = (255, 0, 0, 255)

    def _get_ranking(self, context: Dict[str, Any] = {}) -> List[List[str]]:
        if self.ranking is None:
            self.ranking = context.get('ranking')
            float_values = [
                [float(row[2]), float(row[3]), float(row[4])] for row in self.ranking
            ]
            self.min_s1 = min(fv[0] for fv in float_values)
            self.min_s2 = min(fv[1] for fv in float_values)
            self.min_s3 = min(fv[2] for fv in float_values)
        return self.ranking

    def _get_template_instance_context(self, i: int, context: Dict[str, Any] = {}):
        ranking = self._get_ranking(context)
        if not ranking:
            return super()._get_template_instance_context(i, context)
        row = ranking[i] if 0 <= i < len(ranking) else None
        if not row:
            return {}
        bg_color = self.odd_bg if int(row[0]) % 2 == 1 else self.even_bg
        return {
            'bg_color': bg_color,
            'lap_fg': self.fastest_fg if int(row[0]) == 1 else self.default_fg,
            's1_fg': self.fastest_fg if float(row[2]) == self.min_s1 else self.default_fg,
            's2_fg': self.fastest_fg if float(row[3]) == self.min_s2 else self.default_fg,
            's3_fg': self.fastest_fg if float(row[4]) == self.min_s3 else self.default_fg,
            'row': row
        }
