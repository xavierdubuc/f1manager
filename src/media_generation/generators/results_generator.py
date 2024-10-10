from dataclasses import dataclass

from src.media_generation.generators.abstract_race_generator import \
    AbstractRaceGenerator


@dataclass
class ResultsGenerator(AbstractRaceGenerator):
    visual_type: str = 'results'

    def _get_layout_context(self):
        sup = super()._get_layout_context()
        if not self.race:
            return sup
        return dict(
            sup,
            fastest_lap_driver=self.race.fastest_lap_pilot,
            fastest_lap_team_logo_path=self.race.fastest_lap_pilot.team.get_results_logo_path() if self.race.fastest_lap_pilot else "",
            fastest_lap_driver_name=self.race.fastest_lap_pilot_name.upper() if self.race.fastest_lap_pilot_name else "",
            fastest_lap_point_granted_txt='+1 pt' if self.race.fastest_lap_point_granted() else "",
            fastest_lap_time=self.race.fastest_lap_time,
            fastest_lap_lap=f"TOUR {self.race.fastest_lap_lap}" if self.race.fastest_lap_lap else "",
        )
