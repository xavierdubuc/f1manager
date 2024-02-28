import logging
from dataclasses import dataclass
from typing import List

from src.telemetry.models.enums.ers_deploy_mode import ERSDeployMode
from src.telemetry.models.enums.flag import Flag
from src.telemetry.models.enums.fuel_mix import FuelMix
from src.telemetry.models.enums.traction_control import TractionControl
from src.telemetry.models.enums.tyre import Tyre
from src.telemetry.models.enums.tyre_compound import TyreCompound
from src.telemetry.models.evolving_model import EvolvingModel

_logger = logging.getLogger(__name__)

@dataclass
class CarSetup(EvolvingModel):
    front_wing: int = None
    rear_wing: int = None
    differential_on_throttle: int = None
    differential_off_throttle: int = None
    front_camber: float = None
    rear_camber: float = None
    front_toe: float = None
    rear_toe: float = None
    front_suspension: int = None
    rear_suspension: int = None
    front_anti_roll_bar: int = None
    rear_anti_roll_bar: int = None
    front_suspension_height: int = None
    rear_suspension_height: int = None
    brake_pressure: int = None
    brake_bias: int = None
    rear_left_tyre_pressure: float = None
    rear_right_tyre_pressure: float = None
    front_left_tyre_pressure: float = None
    front_right_tyre_pressure: float = None
    ballast: int = None
    fuel_load: float = None

    def __str__(self):
        return '\n'.join([
            f'Aéro : [{self.front_wing}, {self.rear_wing}]',
            f'Différentiel : [{self.differential_on_throttle}, {self.differential_off_throttle}]',
            f'Géométrie: Carrossage [{round(self.front_camber, 2)}, {round(self.rear_camber, 2)}], Ouvert/Pincement [{round(self.front_toe, 2)}, {round(self.rear_toe, 2)}]',
            f'Suspensions : [{self.front_suspension}, {self.rear_suspension}, {self.front_anti_roll_bar}, {self.rear_anti_roll_bar}, {self.front_suspension_height}, {self.rear_suspension_height}]',
            f'Freins: [{self.brake_pressure}, {self.brake_bias}]',
            f'Pressions: [{round(self.front_left_tyre_pressure,1)}, {round(self.front_right_tyre_pressure, 1)}, {round(self.rear_left_tyre_pressure, 1)}, {round(self.rear_right_tyre_pressure, 1)}]',
            f'{self.fuel_load} L, lest: {self.ballast}'
        ])

    def has_values(self):
        return any(val != 0 for val in [
            self.front_wing,
            self.rear_wing,
            self.differential_on_throttle,
            self.differential_off_throttle,
            self.front_camber,
            self.rear_camber,
            self.front_toe,
            self.rear_toe,
            self.front_suspension,
            self.rear_suspension,
            self.front_anti_roll_bar,
            self.rear_anti_roll_bar,
            self.front_suspension_height,
            self.rear_suspension_height,
            self.brake_pressure,
            self.brake_bias,
            self.rear_left_tyre_pressure,
            self.rear_right_tyre_pressure,
            self.front_left_tyre_pressure,
            self.front_right_tyre_pressure,
            self.ballast,
            self.fuel_load
        ])
