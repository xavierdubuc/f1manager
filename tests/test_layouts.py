from datetime import datetime
import unittest
from config.config import layouts
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.helpers.generator_type import GeneratorType
from src.media_generation.layout.dotted_image_layout import DottedImageLayout
from src.media_generation.models.pilot import Pilot
from src.media_generation.models.team import Team
from src.media_generation.readers.race_reader_models.lineup import LineUp
from src.media_generation.readers.race_reader_models.race import Race, RaceType
from src.media_generation.data import ASPIRANT_TEAM, RESERVIST_TEAM, circuits, teams_idx
from src.media_generation.readers.race_reader_models.race_ranking import RaceRanking, RaceRankingRow


class TestLayouts(unittest.TestCase):
    def setUp(self):
        lineup = LineUp(
            pilot_names=[
                'xCheetah7', 'FBRT_CiD16', 'Iceman7301', 'FBRT_Dinaz-LCK', 'Gros-Nain-Vert', 'FBRT_Sepheldor',
                'FBRT_Majforti', 'TakumiFujiwaraSU', 'arazak_-', 'FBRT_REMBRO', 'FBRT_Nico', 'FBRT_Naax', 'OUDAC-UNNEK',
                'FBRT_Juraptors', 'Enakozi', 'FBRT_DimDim91270', 'OVR_Kayzor', 'FBRT_b0sstyl3', 'Prolactron', 'MoonLight_RR'
            ],
            pilots={
                'xCheetah7': Pilot(name='xCheetah7', team=teams_idx['RedBull'], number='89', title=None, reservist=False, aspirant=False, trigram='CHE'),
                'FBRT_CiD16': Pilot(name='FBRT_CiD16', team=teams_idx['Haas'], number='61', title=None, reservist=False, aspirant=False, trigram='CID'),
                'Iceman7301': Pilot(name='Iceman7301', team=teams_idx['Ferrari'], number='69', title=None, reservist=False, aspirant=False, trigram='ICE'),
                'FBRT_Dinaz-LCK': Pilot(name='FBRT_Dinaz-LCK', team=teams_idx['Ferrari'], number='50', title=None, reservist=False, aspirant=False, trigram='DNZ'),
                'Gros-Nain-Vert': Pilot(name='Gros-Nain-Vert', team=teams_idx['VCARB'], number='5', title=None, reservist=False, aspirant=False, trigram='GRO'),
                'FBRT_Sepheldor': Pilot(name='FBRT_Sepheldor', team=teams_idx['VCARB'], number='21', title=None, reservist=False, aspirant=False, trigram='SEP'),
                'FBRT_Majforti': Pilot(name='FBRT_Majforti', team=teams_idx['Mercedes'], number='90', title=None, reservist=False, aspirant=False, trigram='MAJ'),
                'TakumiFujiwaraSU': Pilot(name='TakumiFujiwaraSU', team=teams_idx['Mercedes'], number='88', title=None, reservist=False, aspirant=False, trigram='TAK'),
                'arazak_-': Pilot(name='arazak_-', team=teams_idx["Williams"], number='6', title=None, reservist=False, aspirant=False, trigram='ARA'),
                'FBRT_REMBRO': Pilot(name='FBRT_REMBRO', team=teams_idx["Williams"], number='78', title=None, reservist=False, aspirant=False, trigram='REM'),
                'FBRT_Nico': Pilot(name='FBRT_Nico', team=teams_idx["McLaren"], number='29', title=None, reservist=False, aspirant=False, trigram='NIC'),
                'FBRT_Naax': Pilot(name='FBRT_Naax', team=teams_idx["McLaren"], number='56', title=None, reservist=False, aspirant=False, trigram='NAX'),
                'OUDAC-UNNEK': Pilot(name='OUDAC-UNNEK', team=teams_idx["AstonMartin"], number='12', title=None, reservist=False, aspirant=False, trigram='OUD'),
                'FBRT_Juraptors': Pilot(name='FBRT_Juraptors', team=teams_idx["AstonMartin"], number='19', title=None, reservist=False, aspirant=False, trigram='JUR'),
                'Enakozi': Pilot(name='Enakozi', team=teams_idx["KickSauber"], number='28', title=None, reservist=False, aspirant=False, trigram='ENA'),
                'FBRT_DimDim91270': Pilot(name='FBRT_DimDim91270', team=teams_idx["KickSauber"], number='91', title=None, reservist=False, aspirant=False, trigram='DIM'),
                'OVR_Kayzor': Pilot(name='OVR_Kayzor', team=teams_idx["Haas"], number='15', title=None, reservist=False, aspirant=False, trigram='KAY'),
                'FBRT_b0sstyl3': Pilot(name='FBRT_b0sstyl3', team=teams_idx["RedBull"], number='8', title=None, reservist=False, aspirant=False, trigram='BOS'),
                'Prolactron': Pilot(name='Prolactron', team=teams_idx["Alpine"], number='26', title=None, reservist=False, aspirant=False, trigram='PRO'),
                'MoonLight_RR': Pilot(name='MoonLight_RR', team=teams_idx["Alpine"], number='98', title=None, reservist=False, aspirant=False, trigram='MOO'),
                'Stewen': Pilot(name='Stewen', team=ASPIRANT_TEAM, number='95', title=None, reservist=False, aspirant=True, trigram='STE'),
                'Redaym': Pilot(name='Redaym', team=RESERVIST_TEAM, number='62', title=None, reservist=True, aspirant=False, trigram='RED'),
            })
        self.race = Race(
            circuit=circuits['Qatar'],
            laps=12,
            full_date=datetime.now(),
            day=2,
            month=9,
            hour="20:45",
            round=1,
            presentation_text="",
            original_lineup=None,
            final_lineup=lineup,
            replacements=None,
            type=RaceType.NORMAL
        )

    # def test_season_pilots_layout(self):
    #     config = GeneratorConfig(
    #         GeneratorType.SEASON_PILOTS,
    #         'tests/test.png',
    #         self.race.final_lineup.pilots,
    #         teams=teams_idx,
    #     )
    #     context = {
    #         'season': 9,
    #         'config': config,
    #         'identifier': 'main'
    #     }
    #     layout = layouts.FBRT["season_pilots"]
    #     img = layout.render(context=context)
    #     img.save('tests/_outputs/season_pilots.png', quality=100)

    # def test_season_teams_layout(self):
    #     config = GeneratorConfig(
    #         GeneratorType.SEASON_TEAMS,
    #         'tests/test.png',
    #         self.race.final_lineup.pilots,
    #         teams=teams_idx,
    #     )
    #     context = {
    #         'season': 9,
    #         'config': config,
    #         'identifier': 'main'
    #     }
    #     layout = layouts.FBRT["season_teams"]
    #     img = layout.render(context=context)
    #     img.save('tests/_outputs/season_teams.png', quality=100)

    # def test_lineup_layout(self):
    #     config = GeneratorConfig(
    #         GeneratorType.LINEUP,
    #         'tests/test.png',
    #         self.race.final_lineup.pilots,
    #         teams=teams_idx,
    #         race=self.race
    #     )
    #     context = {
    #         'season': 9,
    #         'config': config,
    #         'month_fr': 'Septembre',
    #         'race': self.race,
    #         'circuit': self.race.circuit,
    #         'circuit_city': 'LOSAIL',
    #         'teams': teams_idx.values()
    #     }
    #     layout = layouts.FBRT["lineup"]
    #     img = layout.render(context=context)
    #     img.save('tests/_outputs/lineup.png', quality=100)

    # def test_numbers_layout(self):
    #     config = GeneratorConfig(
    #         GeneratorType.NUMBERS,
    #         'tests/test.png',
    #         self.race.final_lineup.pilots,
    #         teams=teams_idx.values(),
    #     )
    #     context = {
    #         'season': 9,
    #         'config': config,
    #         'identifier': 'main'
    #     }
    #     layout = layouts.FBRT["numbers"]
    #     img = layout.render(context=context)
    #     img.save('tests/_outputs/numbers.png', quality=100)

    # def test_result_layout(self):
    #     config = GeneratorConfig(
    #         GeneratorType.RESULTS,
    #         'tests/test.png',
    #         self.race.final_lineup.pilots,
    #         teams=teams_idx,
    #         race=self.race
    #     )
    #     self.race.race_result = RaceRanking([
    #         RaceRankingRow(
    #             position=i+1,
    #             pilot_name=p.name,
    #             split=("51:06.822" if i == 0 else str(round(i*2.345, 3))) if i < 18 else 'NT',
    #             tyres="SHMIW",
    #             best_lap="1.17.671",
    #             points=20-i,
    #             is_driver_of_the_day=i in (1,4),
    #             has_fastest_lap=i in (2, 5),
    #             pilot=p,
    #         )
    #         for i, p in enumerate(self.race.final_lineup.pilots.values())
    #     ])
    #     context = {
    #         'season': 9,
    #         'config': config,
    #         'month_fr': 'Septembre',
    #         'race': self.race,
    #         'circuit': self.race.circuit,
    #         'circuit_city': 'LOSAIL',
    #         'teams': teams_idx.values()
    #     }
    #     layout = layouts.FBRT["results"]
    #     img = layout.render(context=context)
    #     img.save('tests/_outputs/results.png', quality=100)

    # def test_dotted_image_layout(self):
    #     dil = DottedImageLayout(
    #         name='dotted', width=1000, height=90, bg=241,
    #         dots_first_left_top=(20, 14),
    #         round_bottom_left=False,
    #         round_bottom_right=False,
    #     )
    #     img = dil.render()
    #     img.save('tests/_outputs/test.png', quality=100)

    def test_timetrial_layout(self):
        circuit = circuits['Italie']
        ranking = [
            ['1', 'QSL-Rhumsko', '26.153', '25.977', '26.373', '1:18.504'],
            ['2', 'OVR_Kayzor', '26.183', '26.033', '26.454', '1:18.671'],
            ['3', 'Iceman7301', '26.105', '26.092', '26.563', '1:18.762'],
            ['4', 'x0-STEWEN_26-0x', '26.266', '26.078', '26.434', '1:18.779'],
            ['5', 'FBRT_Sepheldor', '26.130', '26.303', '26.502', '1:18.937'],
            ['6', 'arazak_-', '26.199', '26.170', '26.635', '1:19.005'],
            ['7', 'FBRT_Naax', '26.378', '26.128', '26.759', '1:19.266'],
            ['8', 'Nicolas-Nst', '26.255', '26.495', '26.987', '1:19.738'],
            ['9', 'MoonLight_RR', '26.502', '26.641', '26.787', '1:19.932'],
            ['10', 'OUDAC-UNNEK', '26.430', '26.656', '26.845', '1:19.932'],
            ['11', 'FBRT_REMBRO', '26.526', '26.657', '26.758', '1:19.942'],
            ['12', 'TakumiFujiwaraSU', '26.551', '27.316', '27.648', '1:21.516']
        ]
        context = {
            "circuit": circuit,
            "ranking": ranking,
        }
        layout = layouts.FBRT["time_trial"]
        img = layout.render(context=context)
        img.save('tests/_outputs/time_trial.png', quality=100)