from dataclasses import dataclass
import logging
from typing import Tuple
import pandas
from src.gsheet.gsheet import GSheet
from src.media_generation.helpers.generator_type import GeneratorType
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.models.pilot import Pilot
from src.media_generation.models.team import Team
from ..data import teams_idx
from ..data import teams as DEFAULT_TEAMS_LIST


_logger = logging.getLogger(__name__)


@dataclass
class InputData:
    sheet_names: list
    sheet_values: pandas.DataFrame
    sheet_data: pandas.DataFrame = None


class Reader:
    VALUES_SHEET_NAME = '_values'

    def __init__(self, type: GeneratorType, championship_config: dict, season: int,
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
        config = GeneratorConfig(
            type=self.type,
            output=self.out_filepath or f'./output/{self.type.value}.png',
            pilots=pilots,
            teams=teams,
        )
        return config

    def _build_pilots_list(self, values: pandas.DataFrame) -> dict:
        default_team = Team(**self.championship_config['settings']['default_team'])
        reservist_team = Team(**self.championship_config['settings']['reservist_team'])
        return {
            row['Pilotes']: Pilot(
                name=row['Pilotes'],
                team=teams_idx.get(row['Ecurie'], reservist_team if row['Ecurie'] == 'R' else default_team),
                reservist=row['Ecurie'] == 'R',
                number=row['Numéro'],
                trigram=row.get('Trigram')
            ) for _, row in values[values['Pilotes'].notnull()].iterrows()
        }

    def _build_teams_list(self, values: pandas.DataFrame) -> list:
        return [
            teams_idx[row['Ecuries']] for _, row in values.dropna().iterrows()
        ]

    def _read(self) -> Tuple[dict, list]:
        if self.spreadsheet_id:
            input_data = self._get_data_from_gsheet()
        else:
            raise Exception('No spreadsheet id found')

        pilots, teams = self._determine_pilots_and_teams(input_data.sheet_values)
        self.data = input_data.sheet_data
        return pilots, teams

    def _determine_pilots_and_teams(self, sheet_values) -> Tuple[dict, list]:
        if sheet_values is not None:
            if 'Trigram' in sheet_values.columns:
                pilots_values = sheet_values[['Pilotes', 'Numéro', 'Trigram', 'Ecurie']]
            else:
                pilots_values = sheet_values[['Pilotes', 'Numéro', 'Ecurie']]
            pilots = self._build_pilots_list(pilots_values)
            teams_values = sheet_values[['Ecuries']]
            teams = self._build_teams_list(teams_values)
        else:
            pilots = []
            teams = DEFAULT_TEAMS_LIST
        return pilots, teams

    def _get_values_sheet_from_gsheet(self):
        sheet_names = self.google_sheet_service.get_sheet_names(self.spreadsheet_id)

        if self.VALUES_SHEET_NAME in sheet_names:
            vals = self.google_sheet_service.get_sheet_values(self.spreadsheet_id, f'{self.VALUES_SHEET_NAME}!A1:H100')
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
        if self.type in ('results',):
            return all_columns
        return all_columns[:8]  # -> H
