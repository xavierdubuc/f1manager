from typing import Dict
from f1_24_telemetry.packets import CarSetupData
from src.telemetry.models.car_setup import CarSetup
from .abstract_manager import AbstractManager, Change
from ..models.enums.tyre import Tyre

from ..models.enums.tyre_compound import TyreCompound


class CarSetupManager(AbstractManager):
    model = CarSetup

    primitive_fields = {
        'front_wing': 'front_wing',
        'rear_wing': 'rear_wing',
        'differential_on_throttle': 'on_throttle',
        'differential_off_throttle': 'off_throttle',
        'front_camber': 'front_camber',
        'rear_camber': 'rear_camber',
        'front_toe': 'front_toe',
        'rear_toe': 'rear_toe',
        'front_suspension': 'front_suspension',
        'rear_suspension': 'rear_suspension',
        'front_anti_roll_bar': 'front_anti_roll_bar',
        'rear_anti_roll_bar': 'rear_anti_roll_bar',
        'front_suspension_height': 'front_suspension_height',
        'rear_suspension_height': 'rear_suspension_height',
        'brake_pressure': 'brake_pressure',
        'brake_bias': 'brake_bias',
        'rear_left_tyre_pressure': 'rear_left_tyre_pressure',
        'rear_right_tyre_pressure': 'rear_right_tyre_pressure',
        'front_left_tyre_pressure': 'front_left_tyre_pressure',
        'front_right_tyre_pressure': 'front_right_tyre_pressure',
        'ballast': 'ballast',
        'fuel_load': 'fuel_load',
    }
