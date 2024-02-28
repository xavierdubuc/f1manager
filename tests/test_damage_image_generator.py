import unittest

from src.media_generation.damage_image_generator import DamageImageGenerator
from src.telemetry.models.damage import Damage
from src.telemetry.models.participant import Participant


class DamageImageGeneratorTest(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.generator = DamageImageGenerator()

    def test_generate(self):
        names = [
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
            'Xionhearts',
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
        for name in names:
            participant = Participant(name=name)
            damage = Damage(
                tyres_damage=[100, 50, 33, 10],
                diffuser_damage=20,
                floor_damage=70,
                sidepod_damage=20,
                front_left_wing_damage=100,
                front_right_wing_damage=33,
                rear_wing_damage=20
            )
            self.generator.generate(damage, participant)
