from dataclasses import dataclass
from typing import Dict, List
from src.media_generation.helpers.generator_type import GeneratorType
from src.media_generation.models.pilot import Pilot
from src.media_generation.models.team import Team
from src.media_generation.readers.race_reader import RaceReader
from src.media_generation.readers.race_reader_models.race import Race

import logging
_logger = logging.getLogger(__name__)

@dataclass
class CalendarGeneratorConfig:
    races: List[Race]
    season: int
    type: GeneratorType
    output: str


class CalendarReader(RaceReader):
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

    def _get_races_details(self, pilots:Dict[str,Pilot], teams:List[Team]) -> List[Race]:
        sheet_names = self.google_sheet_service.get_sheet_names(self.spreadsheet_id)

        races = []
        for sheet_name in sheet_names:
            if sheet_name[:4] in ('Race', 'Course'):
                _logger.info(f'Dealing with "{sheet_name}"')
                self.sheet_name = sheet_name
                self.data = self._get_data_sheet_from_gsheet()
                race = self._get_race(pilots, teams)
                races.append(race)
        return races
