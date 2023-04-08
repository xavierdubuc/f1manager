import ctypes
import unittest
from unittest.mock import Mock, patch
from f1_22_telemetry.packets import FinalClassificationData
from managers.abstract_manager import Change
from managers.classification_manager import ClassificationManager
from models.classification import Classification
from models.enums.session_type import SessionType
from models.enums.temperature_change import TemperatureChange
from models.enums.track import Track
from models.enums.tyre import Tyre
from models.enums.tyre_compound import TyreCompound
from models.enums.weather import Weather

from models.classification import Classification
from datetime import timedelta


class ClassificationManagerTest(unittest.TestCase):
    def setUp(self):
        super().setUp()

    @patch('managers.abstract_manager.AbstractManager.create')
    def test_create(self, patch_create):
        patch_create.return_value = Classification(
            position=1
        )
        
        packet = FinalClassificationData(
            position=1, num_laps=12, grid_position=2, points=25,
            num_pit_stops=1, result_status=3, best_lap_time_in_ms=1000, total_race_time=12000,
            penalties_time=0, num_penalties=0, num_tyre_stints=2,
            tyre_stints_actual=(ctypes.c_uint8*8)(TyreCompound.c1.value,TyreCompound.c2.value, 0, 0, 0, 0, 0, 0),
            tyre_stints_visual=(ctypes.c_uint8*8)(Tyre.soft.value,Tyre.medium.value, 0, 0, 0, 0, 0, 0),
            tyre_stints_end_laps=(ctypes.c_uint8*8)(1,255,0,0,0,0,0,0)
        )

        classification = ClassificationManager.create(packet)
        patch_create.assert_called_once_with(packet)
        self.assertEqual(classification.tyre_stints_actual, [TyreCompound.c1,TyreCompound.c2])
        self.assertEqual(classification.tyre_stints_visual, [Tyre.soft, Tyre.medium])
        self.assertEqual(classification.tyre_stints_end_laps, [1, 255])

    @patch('managers.abstract_manager.AbstractManager.update')
    def test_update(self, patch_update):
        patch_update.return_value= {}
        packet = FinalClassificationData(
            position=1, num_laps=12, grid_position=2, points=25,
            num_pit_stops=1, result_status=3, best_lap_time_in_ms=1000, total_race_time=12000,
            penalties_time=0, num_penalties=0, num_tyre_stints=2,
            tyre_stints_actual=(ctypes.c_uint8*8)(TyreCompound.c1.value,TyreCompound.c2.value, 0, 0, 0, 0, 0, 0),
            tyre_stints_visual=(ctypes.c_uint8*8)(Tyre.soft.value,Tyre.medium.value, 0, 0, 0, 0, 0, 0),
            tyre_stints_end_laps=(ctypes.c_uint8*8)(1,255,0,0,0,0,0,0)
        )
        classification = ClassificationManager.create(packet)

        new_packet = FinalClassificationData(
            position=1, num_laps=12, grid_position=2, points=25,
            num_pit_stops=1, result_status=3, best_lap_time_in_ms=1000, total_race_time=12000,
            penalties_time=0, num_penalties=0, num_tyre_stints=3,
            tyre_stints_actual=(ctypes.c_uint8*8)(TyreCompound.c1.value,TyreCompound.c2.value, TyreCompound.c3.value, 0, 0, 0, 0, 0),
            tyre_stints_visual=(ctypes.c_uint8*8)(Tyre.soft.value,Tyre.medium.value, Tyre.hard.value, 0, 0, 0, 0, 0),
            tyre_stints_end_laps=(ctypes.c_uint8*8)(1,12,255,0,0,0,0,0)
        )
        changes = ClassificationManager.update(classification, new_packet)
        self.assertEqual(len(changes), 3)
        self.assertIn('tyre_stints_actual', changes)
        self.assertIn('tyre_stints_visual', changes)
        self.assertIn('tyre_stints_end_laps', changes)
        self.assertListEqual(changes['tyre_stints_actual'].actual, classification.tyre_stints_actual)
        self.assertListEqual(changes['tyre_stints_visual'].actual, classification.tyre_stints_visual)
        self.assertListEqual(changes['tyre_stints_end_laps'].actual, classification.tyre_stints_end_laps)
        self.assertEqual(len(classification.tyre_stints_actual), 3)
        self.assertEqual(len(classification.tyre_stints_visual), 3)
        self.assertEqual(len(classification.tyre_stints_end_laps), 3)

        patch_update.return_value= {} # needed to avoid side effects
        nchanges = ClassificationManager.update(classification, new_packet)
        self.assertDictEqual(nchanges, {})