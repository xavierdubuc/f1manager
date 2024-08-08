from datetime import datetime
from typing import Dict, List

import pandas
from src.media_generation.helpers.generator_config import GeneratorConfig

from src.media_generation.helpers.reader import Reader
from src.media_generation.models.pilot import Pilot
from src.media_generation.models.team import Team
from src.media_generation.readers.race_reader_models.lineup import LineUp
from src.media_generation.readers.race_reader_models.race import Race, RaceType
from src.media_generation.readers.race_reader_models.race_ranking import RaceRanking, RaceRankingRow

from ..data import circuits as CIRCUITS

class RaceReader(Reader):
    def read(self) -> GeneratorConfig:
        pilots, teams = self._read()
        race = self._get_race(pilots, teams)
        config = GeneratorConfig(
            type=self.type,
            output=self.out_filepath or f'./output/{self.type.value}.png',
            pilots=pilots,
            teams=teams,
            race=race
        )
        return config

    def _get_data_sheet_from_gsheet(self):
        race_vals = self.google_sheet_service.get_sheet_values(self.spreadsheet_id, f"'{self.sheet_name}'!A1:M45")
        columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L','M']
        return pandas.DataFrame(race_vals[1:], columns=columns)

    def _get_race(self, pilots:Dict[str,Pilot], teams:List[Team]) -> Race:
        race_day = self.data['B'][3]
        if isinstance(race_day, str):
            race_day = datetime.strptime(race_day, '%d/%m')
        original_lineup_names = list(self.data['D'][:20])
        driver_of_the_day_name = self.data['I'][22]
        fastest_lap_pilot_name = self.data['G'][22]

        # REPLACEMENTS
        replacements_frame = self.data[['D', 'E']].where(lambda x: x != '', pandas.NA).dropna()
        # key is replaced by value
        replacements = {
            r['D']: r['E'] for _,r in replacements_frame.iterrows()
        }

        # FINAL LINEUP
        final_lineup_pilots = {}
        for pilot_name in self.data['F'][:20]:
            replaced_pilot_name = None
            for titular, reservist in replacements.items():
                if reservist == pilot_name:
                    replaced_pilot_name = titular
            # not replacing anyone --> just add the pilot to the lineup
            if not replaced_pilot_name:
                if p := pilots.get(pilot_name):
                    final_lineup_pilots[pilot_name] = p
            else:
                # get the replaced pilot's team and create a new pilot with it
                # pilot_name = pilot_name if '/' not in pilot_name else '/'
                replaced_pilot = pilots[replaced_pilot_name]
                p = pilots.get(pilot_name)
                if p:
                    final_lineup_pilots[pilot_name] = Pilot(
                        p.name,
                        replaced_pilot.team if replaced_pilot else None,
                        p.number,
                        p.title,
                        p.reservist,
                        p.trigram
                    )
        final_lineup = LineUp(
            pilot_names=list(self.data['F'][:20]),
            pilots=final_lineup_pilots
        )
        return Race(
            # BASE INFORMATION
            round=self.data['B'][0],
            circuit = CIRCUITS.get(self.data['B'][1], None),
            laps=int(self.data['B'][2] if self.data['B'][2] and self.data['B'][2] != '#N/A' else 0),
            full_date=race_day,
            day=race_day.day,
            month=race_day.strftime('%b'),
            hour = self.data['B'][4],
            presentation_text=self.data['A'][5],
            type = RaceType(self.data['B'][19]),

            # LINE UP
            original_lineup=LineUp(
                pilot_names=original_lineup_names,
                pilots={k:p for k,p in pilots.items() if k in original_lineup_names}
            ),
            replacements=replacements,
            final_lineup=final_lineup,

            # CIRCUIT FASTEST LAP
            circuit_fastest_lap_time = self.data['B'][20],
            circuit_fastest_lap_pilot_name = self.data['B'][21],
            circuit_fastest_lap_season = self.data['B'][22],

            # CIRCUIT LAST WINNER
            circuit_last_winner_name = self.data['B'][23],
            circuit_last_winner_season = self.data['B'][24],

            # RESULTS
            qualification_result = RaceRanking([
                RaceRankingRow(
                    position=i-23,
                    pilot_name=r['B'],
                    split=r['D'],
                    best_lap=r['C'],
                    pilot=final_lineup[r['B']]
                )
                for i, r in self.data[['B','C','D']][26:].iterrows() if r['B']
            ]),
            race_result = RaceRanking([
                RaceRankingRow(
                    position=i+1,
                    pilot_name=r['I'],
                    split=r['J'],
                    tyres=r['K'],
                    best_lap=r['L'],
                    points=int(r['M']),
                    is_driver_of_the_day=r['I']==driver_of_the_day_name,
                    has_fastest_lap=r['I']==fastest_lap_pilot_name,
                    pilot=final_lineup[r['I']],
                )
                for i, r in self.data[['I','J','K','L','M']][:20].iterrows() if r['I']
            ]),

            # FASTEST LAP
            fastest_lap_pilot_name = fastest_lap_pilot_name,
            fastest_lap_pilot = final_lineup[self.data['G'][22]],
            fastest_lap_time = self.data['G'][26],
            fastest_lap_lap = self.data['G'][24],
            driver_of_the_day_name = driver_of_the_day_name,
            driver_of_the_day = final_lineup[driver_of_the_day_name],
            driver_of_the_day_percent = self.data['J'][22],
        )
