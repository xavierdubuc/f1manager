from datetime import datetime
import unittest
from config import layouts
from src.media_generation.models.pilot import Pilot
from src.media_generation.models.team import Team
from src.media_generation.readers.race_reader_models.lineup import LineUp
from src.media_generation.readers.race_reader_models.race import Race, RaceType
from src.media_generation.data import circuits, teams_idx


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
                'FBRT_CiD16': Pilot(name='FBRT_CiD16', team=teams_idx['RedBull'], number='61', title=None, reservist=False, aspirant=False, trigram='CID'),
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
                'FBRT_b0sstyl3': Pilot(name='FBRT_b0sstyl3', team=teams_idx["Haas"], number='8', title=None, reservist=False, aspirant=False, trigram='BOS'),
                'Prolactron': Pilot(name='Prolactron', team=teams_idx["Alpine"], number='26', title=None, reservist=False, aspirant=False, trigram='PRO'),
                'MoonLight_RR': Pilot(name='MoonLight_RR', team=teams_idx["Alpine"], number='98', title=None, reservist=False, aspirant=False, trigram='MOO')
            })
        self.race = Race(
            circuit=circuits['Qatar'],
            laps=12,
            full_date=datetime.now(),
            day=2,
            month=10,
            hour="20:45",
            round=1,
            presentation_text="",
            original_lineup=None,
            final_lineup=lineup,
            replacements=None,
            type=RaceType.NORMAL
        )

    def test_lineup_layout(self):
        context = {
            'month_fr': 'Septembre',
            'race': self.race,
            'teams': teams_idx
        }
        layout = layouts.FBRT["settings"]["layouts"]["lineup"]
        img = layout.render(context=context)
        img.save('tests/test.png', quality=100)
