from dataclasses import dataclass
from src.media_generation.generators.abstract_generator import AbstractGenerator
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.helpers.transform import month_fr
from src.media_generation.models.race_renderer import RaceRenderer
from src.media_generation.readers.race_reader_models.race import Race


@dataclass
class AbstractRaceGenerator(AbstractGenerator):
    def __post_init__(self):
        super().__post_init__()
        self.race: Race = self.config.race
        self.race_renderer: RaceRenderer = RaceRenderer(self.race)

    def _get_layout_context(self):
        ctx = dict(
            super()._get_layout_context(),
            race=self.race,
            circuit=self.race.circuit,
            circuit_country=self.race.circuit.name.upper() if self.race.circuit else "?",
            circuit_city=self.race.circuit.city.upper() if self.race.circuit else "?",
            month_fr=month_fr(self.race.full_date.month-1),
            month_fr_short=month_fr(self.race.full_date.month-1)[:3].upper(),
        )
        if self.race.fastest_lap_pilot:
            ctx.update({
                "fastest_lap_driver": self.race.fastest_lap_pilot,
                "fastest_lap_team_logo_path": self.race.fastest_lap_pilot.team.get_results_logo_path() if self.race.fastest_lap_pilot else "",
                "fastest_lap_driver_name": self.race.fastest_lap_pilot_name.upper() if self.race.fastest_lap_pilot_name else "",
                "fastest_lap_point_granted_txt": '+1 pt' if self.race.fastest_lap_point_granted() else "",
                "fastest_lap_time": self.race.fastest_lap_time,
                "fastest_lap_lap": f"TOUR {self.race.fastest_lap_lap}" if self.race.fastest_lap_lap else "",
            })
        if self.race.driver_of_the_day:
            ctx.update({
                "driver_of_the_day": self.race.driver_of_the_day,
                "driver_of_the_day_name": self.race.driver_of_the_day_name.upper() if self.race.driver_of_the_day_name else ""
            })
            if pct := self.race.driver_of_the_day_percent:
                ctx.update({
                    "driver_of_the_day_percent": f"{int(float(pct[:-1].replace(',','.')))}%"
                })
        return ctx
