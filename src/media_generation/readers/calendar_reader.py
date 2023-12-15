from dataclasses import dataclass
from typing import List
from src.media_generation.helpers.generator_type import GeneratorType
from src.media_generation.readers.all_races_reader import AllRacesReader
from src.media_generation.readers.race_reader_models.race import Race


@dataclass
class CalendarGeneratorConfig:
    races: List[Race]
    season: int
    type: GeneratorType
    output: str


class CalendarReader(AllRacesReader):
    def read(self):
        pilots, teams = self._read()
        races = self._get_races_details(pilots, teams)
        config = CalendarGeneratorConfig(
            type=self.type,
            season=self.season,
            races=races,
            output=self.out_filepath or f'./output/{self.type}.png',
        )
        return config