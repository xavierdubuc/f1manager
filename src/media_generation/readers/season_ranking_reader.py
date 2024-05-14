from dataclasses import dataclass
from typing import List
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.readers.all_races_reader import AllRacesReader
from src.media_generation.readers.race_reader_models.race import Race


@dataclass
class SeasonRankingGeneratorConfig(GeneratorConfig):
    races: List[Race] = None


class SeasonRankingReader(AllRacesReader):
    def read(self):
        pilots, teams = self._read()
        races = self._get_races_details(pilots, teams)
        config = SeasonRankingGeneratorConfig(
            type=self.type,
            output=self.out_filepath or f'./output/{self.type.value}.png',
            pilots=pilots,
            teams=teams,
            races=races
        )
        return config
