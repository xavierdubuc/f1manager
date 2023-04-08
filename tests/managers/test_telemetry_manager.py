import ctypes
import unittest
from unittest.mock import patch
from f1_22_telemetry.packets import CarTelemetryData
from managers.telemetry_manager import TelemetryManager

from models.telemetry import Telemetry


class TelemetryManagerTest(unittest.TestCase):
    def setUp(self):
        super().setUp()

    @patch('managers.abstract_manager.AbstractManager.create')
    def test_create(self, patch_create):
        patch_create.return_value = Telemetry(
            speed=300
        )

        packet = CarTelemetryData(
            speed=300,
            throttle=0.5,
            steer=0.2,
            brake=0.3,
            clutch=93,
            gear=4,
            engine_rpm=10234,
            drs=0,
            rev_lights_percent=22,
            engine_temperature=252,
            brakes_temperature=(ctypes.c_uint16 * 4)(500, 125, 125, 500),
            tyres_surface_temperature=(ctypes.c_uint8 * 4)(102, 102, 101, 103),
            tyres_inner_temperature=(ctypes.c_uint8 * 4)(98, 98, 97, 97),
            tyres_pressure=(ctypes.c_float * 4)(22.4, 22.4, 23.5, 23.5),
            surface_type=(ctypes.c_uint8 * 4)(1, 1, 2, 2),
        )

        telemetry = TelemetryManager.create(packet)
        patch_create.assert_called_once_with(packet)
        self.assertListEqual(telemetry.brakes_temperature, [500, 125, 125, 500])
        self.assertListEqual(telemetry.tyres_surface_temperature, [102, 102, 101, 103])
        self.assertListEqual(telemetry.tyres_inner_temperature, [98, 98, 97, 97])
        self.assertAlmostEqual(telemetry.tyres_pressure[0], 22.4, places=2)
        self.assertAlmostEqual(telemetry.tyres_pressure[1], 22.4, places=2)
        self.assertAlmostEqual(telemetry.tyres_pressure[2], 23.5, places=2)
        self.assertAlmostEqual(telemetry.tyres_pressure[3], 23.5, places=2)
        self.assertListEqual(telemetry.surface_type, [1, 1, 2, 2])

    @patch('managers.abstract_manager.AbstractManager.update')
    def test_update(self, patch_update):
        patch_update.return_value = {}
        packet = CarTelemetryData(
            speed=300,
            throttle=0.5,
            steer=0.2,
            brake=0.3,
            clutch=93,
            gear=4,
            engine_rpm=10234,
            drs=0,
            rev_lights_percent=22,
            engine_temperature=252,
            brakes_temperature=(ctypes.c_uint16 * 4)(500, 125, 125, 500),
            tyres_surface_temperature=(ctypes.c_uint8 * 4)(102, 102, 101, 103),
            tyres_inner_temperature=(ctypes.c_uint8 * 4)(98, 98, 97, 97),
            tyres_pressure=(ctypes.c_float * 4)(22.4, 22.4, 23.5, 23.5),
            surface_type=(ctypes.c_uint8 * 4)(1, 1, 2, 2),
        )
        telemetry = TelemetryManager.create(packet)

        new_packet = CarTelemetryData(
            speed=300,
            throttle=0.5,
            steer=0.2,
            brake=0.3,
            clutch=93,
            gear=4,
            engine_rpm=10234,
            drs=0,
            rev_lights_percent=22,
            engine_temperature=252,
            brakes_temperature=(ctypes.c_uint16 * 4)(500, 225, 125, 500),
            tyres_surface_temperature=(ctypes.c_uint8 * 4)(102, 202, 101, 103),
            tyres_inner_temperature=(ctypes.c_uint8 * 4)(98, 98, 47, 97),
            tyres_pressure=(ctypes.c_float * 4)(22.4, 22.4, 23.2, 23.5),
            surface_type=(ctypes.c_uint8 * 4)(2, 2, 1, 1),
        )

        changes = TelemetryManager.update(telemetry, new_packet)
        self.assertEqual(len(changes), 5)
        self.assertIn('brakes_temperature', changes)
        self.assertIn('tyres_surface_temperature', changes)
        self.assertIn('tyres_inner_temperature', changes)
        self.assertIn('tyres_pressure', changes)
        self.assertIn('surface_type', changes)
        self.assertEqual(changes['brakes_temperature'].actual, telemetry.brakes_temperature)
        self.assertEqual(changes['tyres_surface_temperature'].actual, telemetry.tyres_surface_temperature)
        self.assertEqual(changes['tyres_inner_temperature'].actual, telemetry.tyres_inner_temperature)
        self.assertEqual(changes['tyres_pressure'].actual, telemetry.tyres_pressure)
        self.assertEqual(changes['surface_type'].actual, telemetry.surface_type)
        self.assertListEqual(telemetry.brakes_temperature, [500, 225, 125, 500])
        self.assertListEqual(telemetry.tyres_surface_temperature, [102, 202, 101, 103])
        self.assertListEqual(telemetry.tyres_inner_temperature, [98, 98, 47, 97])
        self.assertAlmostEqual(telemetry.tyres_pressure[0], 22.4, places=2)
        self.assertAlmostEqual(telemetry.tyres_pressure[1], 22.4, places=2)
        self.assertAlmostEqual(telemetry.tyres_pressure[2], 23.2, places=2)
        self.assertAlmostEqual(telemetry.tyres_pressure[3], 23.5, places=2)
        self.assertListEqual(telemetry.surface_type, [2, 2, 1, 1])

        patch_update.return_value = {}  # needed to avoid side effects
        nchanges = TelemetryManager.update(telemetry, new_packet)

        self.assertDictEqual(nchanges, {})
