import pandas
from src.media_generation.generators.exceptions import IncorrectDataException
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.helpers.generator_type import GeneratorType

from src.media_generation.helpers.reader import Reader
from src.media_generation.readers.general_ranking_models.pilot_ranking import PilotRanking, PilotRankingRow
from src.media_generation.readers.general_ranking_models.race_result import RaceResult
from src.media_generation.readers.general_ranking_models.ranking import Ranking
from src.media_generation.readers.general_ranking_models.team_ranking import TeamRanking, TeamRankingRow
from src.media_generation.data import teams_idx as TEAMS

class GeneralRankingReader(Reader):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metric = kwargs.get('metric', 'Total')
        if self.type in (GeneratorType.PILOTS_RANKING, GeneratorType.LICENSE_POINTS):
            self.sheet_name = 'Pilots Ranking'
        elif self.type == GeneratorType.TEAMS_RANKING:
            self.sheet_name = 'Teams Ranking'
        else:
            raise IncorrectDataException(f'{self.type.value} is not supported by GeneralRankingReader !')

    def read(self):
        pilots, teams = self._read()
        ranking = self._get_general_ranking(pilots, teams)
        max_size = -1
        self.data = self.data.where(self.data != 'abs', pandas.NA)
        if self.type == GeneratorType.TEAMS_RANKING:
            self.data = self.data.where(self.data != '0', pandas.NA)

        # DETERMINE max_size
        for i, row in self.data.iterrows():
            if i == 0: # ignore first line as it's only the circuit names
                continue
            r = row.dropna()
            max_size = max_size if max_size > r.size else r.size
        if self.type == GeneratorType.TEAMS_RANKING:
            ranking_title = f'Saison {self.season} classement équipes'.upper()
            ranking_subtitle = f'après {self.data.columns[max_size-1]}'.upper() if max_size > 2 else None
            ranking.amount_of_races = int(self.data.columns[max_size-1].split(' ')[-1]) if max_size > 2 else 0
        else:
            if self.metric == 'Total':
                ranking_title = f'Saison {self.season} classement pilotes'.upper()
            elif self.metric == 'Permis':
                ranking_title = f'Saison {self.season} points de permis'.upper()
            else:
                ranking_title = f'Saison {self.season} pilotes points/course'.upper()
            ranking_subtitle = f'après {self.data.columns[max_size-1]}'.upper() if max_size > 7 else None
            ranking.amount_of_races = int(self.data.columns[max_size-1].split(' ')[-1]) if max_size > 7 else 0

        config = GeneratorConfig(
            type=self.type,
            metric=self.metric,
            output=self.out_filepath or f'./output/{self.type.value}.png',
            pilots=pilots,
            teams=teams,
            ranking=ranking,
            ranking_title=ranking_title,
            ranking_subtitle=ranking_subtitle,
        )
        return config

    def _get_data_sheet_from_gsheet(self):
        range_str = f"'{self.sheet_name}'!A1:U50"  # TODO --> config
        vals = self.google_sheet_service.get_sheet_values(self.spreadsheet_id, range_str)
        columns = vals[0] 
        values = [
            row + ([None] * (len(columns) - len(row)))
            for row in vals[1:]
        ]
        return pandas.DataFrame(values, columns=vals[0])

    def _get_general_ranking(self, pilots, teams) -> Ranking:
        if self.type == GeneratorType.TEAMS_RANKING:
            return self._get_teams_general_ranking(teams)
        return self._get_pilots_general_ranking(pilots)

    def _get_teams_general_ranking(self, teams:list) -> TeamRanking:
        ranking = TeamRanking(
            rows=[
                TeamRankingRow(
                    team_name=row.iloc[0],
                    team=TEAMS[row.iloc[0]],
                    total_points=int(row.iloc[1].replace(',','.')),
                    race_results=[
                        RaceResult(
                            race_number=race_name.replace('Course ',''),
                            points=int(result)
                        )
                        for race_name, result in row.iloc[2:16].items()
                    ]
                ) for _, row in self.data.iterrows()
            ]
        )
        return ranking

    def _get_pilots_general_ranking(self, pilots:dict) -> PilotRanking:
        dataset = self.data[self.data['Pilot'] != '']
        ranking = PilotRanking(
            rows=[
                PilotRankingRow(
                    pilot_name=row.iloc[0],
                    pilot=pilots[row.iloc[0]],
                    titular=row.iloc[1] == 'TRUE',
                    team_name=row.iloc[2],
                    total_points=int(row.iloc[3].replace(',','.')),
                    mean_points=float(row.iloc[4].replace(',','.')),
                    license_points=int(row.iloc[5]),
                    amount_of_races=int(row.iloc[6]),
                    race_results=[
                        RaceResult(
                            race_number=race_name.replace('Course ',''),
                            points=int(result) if result not in ('abs', 'NT', 'DSQ') else result
                        )
                        for race_name, result in row.iloc[7:].items()
                    ]
                ) for i, row in dataset.iterrows() if row.iloc[1] is not None
            ]
        )

        return ranking
