import pandas
from src.media_generation.helpers.generator_config import GeneratorConfig, GeneratorType

from src.media_generation.helpers.reader import Reader
from src.media_generation.readers.pilot_ranking import PilotRanking, PilotRankingRow
from src.media_generation.readers.race_result import RaceResult
from src.media_generation.readers.ranking import Ranking
from src.media_generation.readers.team_ranking import TeamRanking, TeamRankingRow

class GeneralRankingReader(Reader):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metric = kwargs.get('metric', 'Total')
        if self.type in (GeneratorType.PilotsRanking.value, GeneratorType.LicensePoints.value):
            self.sheet_name = 'Pilots Ranking'
        if self.type == GeneratorType.TeamsRanking.value:
            self.sheet_name = 'Teams Ranking'

    def read(self):
        pilots, teams = self._read()
        ranking = self._get_general_ranking()
        max_size = -1
        self.data = self.data.where(self.data != 'abs', pandas.NA)
        if self.type == GeneratorType.TeamsRanking.value:
            self.data = self.data.where(self.data != '0', pandas.NA)
        for i, row in self.data.iterrows():
            r = row.dropna()
            max_size = max_size if max_size > r.size else r.size
        if self.type in (GeneratorType.PilotsRanking.value, GeneratorType.LicensePoints.value):
            if self.metric == 'Total':
                ranking_title = f'Saison {self.season} classement pilotes'.upper()
            else:
                ranking_title = f'Saison {self.season} pilotes points/course'.upper()
        elif self.type == GeneratorType.TeamsRanking.value:
            ranking_title = f'Saison {self.season} classement équipes'.upper()
        ranking_subtitle = f'après {self.data.columns[max_size-1]}'.upper()
            
        config = GeneratorConfig(
            type=self.type,
            metric=self.metric,
            output=self.out_filepath or f'./output/{self.type}.png',
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

    def _get_general_ranking(self) -> Ranking:
        if self.type == GeneratorType.TeamsRanking.value:
            return self._get_teams_general_ranking()
        return self._get_pilots_general_ranking()

    def _get_teams_general_ranking(self) -> TeamRanking:
        ranking = TeamRanking(
            rows=[
                TeamRankingRow(
                    team_name=row.iloc[0],
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

    def _get_pilots_general_ranking(self) -> PilotRanking:
        dataset = self.data[self.data['Pilot'] != '']
        ranking = PilotRanking(
            rows=[
                PilotRankingRow(
                    pilot_name=row.iloc[0],
                    titular=bool(row.iloc[1]),
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
                        for race_name, result in row.iloc[6:].items()
                    ]
                ) for _, row in dataset.iterrows()
            ]
        )

        return ranking