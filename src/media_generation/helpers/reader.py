from dataclasses import dataclass
from datetime import datetime
import logging
import pandas
from src.gsheet.gsheet import GSheet
from src.media_generation.helpers.generator_config import FastestLap, GeneratorConfig
from src.media_generation.models import Pilot, Race
from src.media_generation.models.team import Team
from ..data import circuits, teams_idx
from ..data import teams as DEFAULT_TEAMS_LIST



_logger = logging.getLogger(__name__)


@dataclass
class InputData:
    sheet_names: list
    sheet_values: pandas.DataFrame
    sheet_data: pandas.DataFrame = None


class Reader:
    VALUES_SHEET_NAME = '_values'
    DEFAULT_SPREADSHEET_ID = '1JJw3YnVUXYCyjhH4J5MIbVg5OtjTIDLptx0pF2M9KV4'

    def __init__(self, type: str, championship_config: dict, season: int,
                 out_filepath: str = None, sheet_name: str = None, *args, **kwargs):
        self.type = type
        self.championship_config = championship_config
        self.season = season
        self.out_filepath = out_filepath
        self.sheet_name = sheet_name
        self.season_config = championship_config['seasons'][self.season]
        self.spreadsheet_id = self.season_config['sheet']
        self.google_sheet_service = GSheet()

    def read(self):
        pilots, teams = self._read()
        race = self._get_race(pilots, teams) if self.type not in ('numbers', 'season_lineup', 'pilot') else None
        config = GeneratorConfig(
            type=self.type,
            output=self.out_filepath or f'./output/{self.type}.png',
            pilots=pilots,
            teams=teams,
            race=race
        )
        if self.type == 'presentation':
            config.description = self.data['A'][6]
        if self.type in ('pole', 'grid_ribbon'):
            config.qualif_ranking = self.data[['B','C']][24:]
        if self.type in ('results', 'fastest'):
            config.ranking = self._get_ranking()
        if self.type == 'results':
            config.driver_of_the_day = self._get_driver_of_the_day()
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
        default_team = Team(**self.championship_config['settings']['default_team'])
        reservist_team = Team(**self.championship_config['settings']['reservist_team'])
        return {
            row['Pilotes']: Pilot(
                name=row['Pilotes'],
                team=teams_idx.get(row['Ecurie'], reservist_team if row['Ecurie'] == 'R' else default_team),
                reservist=row['Ecurie'] == 'R',
                number=row['Numéro']
            ) for _, row in values[values['Pilotes'].notnull()].iterrows()
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
            pilots = []
            teams = DEFAULT_TEAMS_LIST
        return pilots, teams

    def _get_race(self, pilots, teams):
        race_day = self.data['B'][3]
        if isinstance(race_day, str):
            race_day = datetime.strptime(race_day, '%d/%m')
        hour = self.data['B'][4]

        return Race(
            full_date=race_day,
            round=self.data['B'][0],
            laps=int(self.data['B'][2]),
            circuit=circuits[self.data['B'][1]],
            day=race_day.day,
            month=race_day.strftime('%b'),
            hour=hour,
            pilots=pilots,
            teams=teams,
            type=self.data['B'][20],
            swappings=self._determine_swappings(pilots)
        )

    def _get_ranking(self):
        ranking_cols = ['I', 'J', 'K', 'L']
        return self.data[ranking_cols][:20]

    def _get_driver_of_the_day(self):
        return self.data['I'][22]

    def _get_fastest_lap(self, race: Race):
        vals = {'pilot_name': self.data['G'][22]}
        if self.type == 'results':
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
            vals = self.google_sheet_service.get_sheet_values(self.spreadsheet_id, '_values!A1:G100')
            sheet_values = pandas.DataFrame(vals[1:], columns=vals[0])
        else:
            sheet_values = None
        return sheet_values

    def _get_data_sheet_from_gsheet(self):
        race_vals = self.google_sheet_service.get_sheet_values(self.spreadsheet_id, f"'{self.sheet_name}'!A1:L45")
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
        if self.type in ('results', 'fastest'):
            return all_columns
        return all_columns[:8]  # -> H
