from dataclasses import dataclass
from datetime import datetime
import logging
import os.path
import pandas
from src.gsheet.gsheet import GSheet
from src.media_generation.helpers.generator_config import FastestLap, GeneratorConfig
from src.media_generation.models import Pilot, Race
from ..data import circuits, teams_idx
from ..data import (
    teams as DEFAULT_TEAMS_LIST,
    pilots as DEFAULT_PILOTS_LIST,
    DEFAULT_TEAM,
    RESERVIST_TEAM
)


_logger = logging.getLogger(__name__)


@dataclass
class InputData:
    sheet_names: list
    sheet_values: pandas.DataFrame
    sheet_data: pandas.DataFrame = None


class Reader:
    VALUES_SHEET_NAME = '_values'
    DEFAULT_SPREADSHEET_ID = '1JJw3YnVUXYCyjhH4J5MIbVg5OtjTIDLptx0pF2M9KV4'

    def __init__(self, type: str,
                 filepath: str = 'gsheet:1JJw3YnVUXYCyjhH4J5MIbVg5OtjTIDLptx0pF2M9KV4',
                 sheet_name: str = None, out_filepath: str = None):
        self.filepath = filepath
        if self.filepath.startswith('gsheet'):
            parts = self.filepath.split(':')
            self.spreadsheet_id = parts[1] if len(parts) > 1 else self.DEFAULT_SPREADSHEET_ID
        else:
            self.spreadsheet_id = None
        self.sheet_name = sheet_name
        self.type = type
        self.out_filepath = out_filepath
        self.google_sheet_service = GSheet()

    def read(self):
        pilots, teams = self._read()
        race = self._get_race(pilots, teams) if self.type not in ('numbers', 'season_lineup') else None
        config = GeneratorConfig(
            type=self.type,
            output=self.out_filepath or f'./output/{self.type}.png',
            pilots=pilots,
            teams=teams,
            race=race
        )
        if self.type == 'presentation':
            config.description = self.data['A'][6]
        if self.type in ('pole', 'grid'):
            config.qualif_ranking = [
                race.get_pilot(self.data['G'][29]),
                race.get_pilot(self.data['G'][30]),
                race.get_pilot(self.data['G'][31]),
            ]
        if self.type in ('results', 'details', 'fastest', 'grid'):
            config.ranking = self._get_ranking()
        if self.type in ('results', 'details'):
            config.fastest_lap = self._get_fastest_lap(race)
        return config

    def _determine_swappings(self, pilots):
        replacements = self.data[['D', 'E']].where(lambda x: x != '', pandas.NA).dropna()
        out = {}
        for _, row in replacements.iterrows():
            subs = row['E']
            while out.get(subs) and len(subs) < 22:
                subs += ' '
            out[subs] = pilots.get(row['D'])
        return out

    def _build_pilots_list(self, values: pandas.DataFrame):
        return {
            row['Pilotes']: Pilot(name=row['Pilotes'], team=teams_idx.get(
                row['Ecurie'], RESERVIST_TEAM if row['Ecurie'] == 'R' else DEFAULT_TEAM), number=row['Numéro'])
            for _, row in values[values['Pilotes'].notnull()].iterrows()
        }

    def _build_teams_list(self, values: pandas.DataFrame):
        return [
            teams_idx[row['Ecuries']] for _, row in values.dropna().iterrows()
        ]

    def _read(self):
        if self.spreadsheet_id:
            input_data = self._get_data_from_gsheet()
        else:
            raise Exception('No spreadsheet id found')

        pilots, teams = self._determine_pilots_and_teams(input_data.sheet_values)
        self.data = input_data.sheet_data
        return pilots, teams

    def _determine_pilots_and_teams(self, sheet_values):
        if sheet_values is not None:
            pilots_values = sheet_values[['Pilotes', 'Numéro', 'Ecurie']]
            pilots = self._build_pilots_list(pilots_values)
            teams_values = sheet_values[['Ecuries']]
            teams = self._build_teams_list(teams_values)
        else:
            pilots = DEFAULT_PILOTS_LIST
            teams = DEFAULT_TEAMS_LIST
        return pilots, teams

    def _get_race(self, pilots, teams):
        race_day = self.data['B'][3]
        if isinstance(race_day, str):
            race_day = datetime.strptime(race_day, '%d/%m')
        hour = self.data['B'][4]
        if isinstance(hour, str):
            hour = datetime.strptime(hour, '%H:%M')

        return Race(
            round=self.data['B'][0],
            laps=int(self.data['B'][2]),
            circuit=circuits[self.data['B'][1]],
            day=race_day.day,
            month=race_day.strftime('%b'),
            hour=hour.strftime('%H.%M'),
            pilots=pilots,
            teams=teams,
            type=self.data['B'][20],
            swappings=self._determine_swappings(pilots)
        )

    def _get_ranking(self):
        ranking_cols = ['I', 'J', 'K', 'L']
        if self.type == 'results':
            ranking_cols = 'I'
        return self.data[ranking_cols][:20]

    def _get_fastest_lap(self, race: Race):
        vals = {'pilot_name': self.data['G'][22]}
        if self.type == 'details':
            vals.update({
                'lap': self.data['G'][24],
                'time': self.data['G'][26]}
            )

        return FastestLap(
            pilot=race.get_pilot(vals['pilot_name']),
            lap=vals.get('lap'),
            time=vals.get('time')
        )

    def _get_values_sheet_from_gsheet(self):
        sheet_names = self.google_sheet_service.get_sheet_names(self.spreadsheet_id)

        if self.VALUES_SHEET_NAME in sheet_names:
            vals = self.google_sheet_service.get_sheet_values(self.spreadsheet_id, '_values!A1:G30')
            sheet_values = pandas.DataFrame(vals[1:], columns=vals[0])
        else:
            sheet_values = None
        return sheet_values

    def _get_data_sheet_from_gsheet(self):
        race_vals = self.google_sheet_service.get_sheet_values(self.spreadsheet_id, f"'{self.sheet_name}'!A1:L33")
        max_len = max([len(race_val) for race_val in race_vals[1:]])
        columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'][:max_len]
        return pandas.DataFrame(race_vals[1:], columns=columns)

    def _get_data_from_gsheet(self) -> InputData:
        sheet_names = self.google_sheet_service.get_sheet_names(self.spreadsheet_id)
        sheet_values = self._get_values_sheet_from_gsheet()

        if not self.sheet_name:
            sheet_data = None
        else:
            if self.sheet_name not in sheet_names:
                raise Exception(
                    f'{self.sheet_name} is not a valid sheet name, please select a sheet within possible values : {sheet_names}')
            sheet_data = self._get_data_sheet_from_gsheet()

        _logger.info(f'Data have been read from google spreadsheet "{self.spreadsheet_id}"')
        return InputData(
            sheet_names=sheet_names,
            sheet_values=sheet_values,
            sheet_data=sheet_data
        )

    def _get_sheet_columns(self) -> list:
        all_columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        if self.type in ('details', 'fastest'):
            return all_columns
        if self.type == 'results':
            return all_columns[:9]  # -> I
        return all_columns[:8]  # -> H
