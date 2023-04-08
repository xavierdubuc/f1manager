import unittest
from unittest.mock import patch
from f1_22_telemetry.packets import LapData
from managers.lap_manager import LapManager

from models.lap import Lap


class LapManagerTest(unittest.TestCase):
    def setUp(self):
        super().setUp()

    @patch('managers.abstract_manager.AbstractManager.create')
    def test_create(self, patch_create):
        patch_create.return_value = Lap(
            car_position=1
        )

        packet = LapData()

        lap = LapManager.create(packet, 1)
        patch_create.assert_called_once_with(packet)
        self.assertEqual(lap.index, 1)