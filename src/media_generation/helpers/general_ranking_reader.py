import pandas
from .generator_config import GeneratorType
from .generator_config import GeneratorConfig
from .reader import Reader

class GeneralRankingReader(Reader):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metric = kwargs['metric']
        if type == GeneratorType.PilotsRanking.value:
            self.sheet_name = 'Pilots Ranking'
        if type == GeneratorType.TeamsRanking.value:
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
        if self.type == GeneratorType.PilotsRanking.value:
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
        range_str = f"'{self.sheet_name}'!A1:S50"
        vals = self.google_sheet_service.get_sheet_values(self.spreadsheet_id, range_str)
        columns = vals[0] 
        values = [
            row + ([None] * (len(columns) - len(row)))
            for row in vals[1:]
        ]
        return pandas.DataFrame(values, columns=vals[0])

    def _get_general_ranking(self):
        A = 'Ecurie' if self.type == GeneratorType.TeamsRanking.value else 'Pilot'
        columns = [A,'Total'] if self.type == GeneratorType.TeamsRanking.value else [A,'Total', 'Points par course']
        return self.data[columns].where(lambda x: x != '', pandas.NA).dropna()