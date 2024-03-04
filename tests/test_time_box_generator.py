import unittest

from src.media_generation.time_box_generator import TimeBoxGenerator
from src.telemetry.models.car_status import CarStatus
from src.telemetry.models.damage import Damage
from src.telemetry.models.enums.team import Team
from src.telemetry.models.enums.tyre import Tyre
from src.telemetry.models.lap import Lap
from src.telemetry.models.lap_record import LapRecord
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session


class TimeBoxGeneratorTest(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.generator = TimeBoxGenerator()

    def test_generate(self):
        names = [
            'Xionhearts',
            'FBRT_Seb07',
            'Enakozi',
            'majforti-07',
            'FBRT_DimDim91270',
            'Gros-Nain-Vert',
            'FBRT_REMBRO',
            'FBRT_CiD16',
            'FBRT_Naax',
            'DiNaZ-LCK',
            'Juraptors',
            'WSC_Gregy21',
            'FBRT_Kayzor',
            'b0sS-sTyl3dimi',
            'Iceman7301',
            'MoonLight_RR',
            'RSC-Mooky79',
            'Arnud_30',
            'x0-STEWEN_26-0x',
            'APX_Maxeagle',
            'VRA-RedAym62',
            'ewocflo',
            'TheLoulou29',
            'krueger-_-freddy',
            'djeck',
            'F1TEAM_Dadoye',
            'GT10_LeMac',
            'TakumiFujiwaraSU',
            'OUDAC-UNNEK',
            'chriss_29',
            'Nicolas-Nst',
        ]
        tyres = [Tyre(i) for i in (16,17,18,7,8)]
        teams = [Team(i) for i in range(10)]
        session = Session(current_fastest_lap=90000, current_fastest_sector1=29000, current_fastest_sector2=30000, current_fastest_sector3=31000)
        for i,name in enumerate(names):
            participant = Participant(name=name, team=teams[i%10])
            car_status = CarStatus(visual_tyre_compound=tyres[i%5])
            lap = Lap(car_position=i+1, sector_1_time_in_ms=28001, sector_2_time_in_ms=30200, current_lap_time_in_ms=90200)
            lap_record = LapRecord()
            self.generator.generate(lap, lap_record, participant, car_status, session)
