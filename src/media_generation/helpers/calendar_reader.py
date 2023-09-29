from dataclasses import dataclass
from datetime import datetime
import pandas

from src.media_generation.models.race import Race
from .reader import Reader
from ..data import circuits as CIRCUITS

@dataclass
class CalendarGeneratorConfig:
    races: list
    season: int
    type: str
    output: str


class CalendarReader(Reader):
    def read(self):
        races = self._get_races_details()
            
        config = CalendarGeneratorConfig(
            type=self.type,
            season=self.season,
            races=races,
            output=self.out_filepath or f'./output/{self.type}.png',
        )
        return config

    def _get_races_details(self):
        sheet_names = self.google_sheet_service.get_sheet_names(self.spreadsheet_id)

        races = []
        for sheet_name in sheet_names:
            if sheet_name[:4] == 'Race':
                race_vals = self.google_sheet_service.get_sheet_values(self.spreadsheet_id, f"'{sheet_name}'!A1:B22")
                df = pandas.DataFrame(race_vals[1:], columns=['A','B'])
                date_obj = datetime.strptime(f"{df['B'][3]}/{datetime.now().year}", '%d/%m/%Y').date()
                race = {
                    'index': df['B'][0],
                    'circuit': CIRCUITS.get(df['B'][1], None),
                    'type': df['B'][19],
                    'date': date_obj,
                    'hour': df['B'][4],
                    'obj': Race(
                        full_date = date_obj,
                        round=df['B'][0],
                        laps=int(df['B'][2]),
                        circuit=CIRCUITS.get(df['B'][1]),
                        day='dummy',
                        month='value',
                        hour=df['B'][4],
                        pilots={},
                        teams=[],
                        type=df['B'][19]
                    )
                }
                races.append(race)

        return races
