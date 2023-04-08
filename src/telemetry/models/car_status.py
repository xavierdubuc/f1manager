from datetime import timedelta
import logging
from dataclasses import dataclass
from f1_22_telemetry.packets import CarStatusData
from models.evolving_model import EvolvingModel
from models.enums.traction_control import TractionControl
from models.enums.fuel_mix import FuelMix
from models.enums.tyre_compound import TyreCompound
from models.enums.tyre import Tyre
from models.enums.flag import Flag
from models.enums.ers_deploy_mode import ERSDeployMode

_logger = logging.getLogger(__name__)

ERS_CAPACITY_JOUL = 4000000

@dataclass
class CarStatus(EvolvingModel):
    traction_control: TractionControl = None
    fuel_mix: FuelMix = None
    actual_tyre_compound: TyreCompound = None
    visual_tyre_compound: Tyre = None
    vehicle_fia_flags: Flag = None
    ers_deploy_mode: ERSDeployMode = None
    anti_lock_brakes_enabled: bool = None
    pit_limiter_enabled: bool = None
    drs_allowed: bool = None
    network_paused: bool = None
    front_brake_bias: int = None
    fuel_in_tank: float = None
    fuel_capacity: float = None
    fuel_remaining_laps: float = None
    max_rpm: int = None
    idle_rpm: int = None
    max_gears: int = None
    drs_activation_distance: int = None  # meters
    tyres_age_laps: int = None
    ers_store_energy: float = None
    ers_harvested_this_lap_mguk: float = None
    ers_harvested_this_lap_mguh: float = None
    ers_deployed_this_lap: float = None

    @staticmethod
    def _get_primitive_field_names():
        return {
            "front_brake_bias": "front_brake_bias",
            "fuel_in_tank": "fuel_in_tank",
            "fuel_capacity": "fuel_capacity",
            "fuel_remaining_laps": "fuel_remaining_laps",
            "max_rpm": "max_rpm",
            "idle_rpm": "idle_rpm",
            "max_gears": "max_gears",
            "drs_activation_distance": "drs_activation_distance",
            "tyres_age_laps": "tyres_age_laps",
            "ers_store_energy": "ers_store_energy",
            "ers_harvested_this_lap_mguk": "ers_harvested_this_lap_mguk",
            "ers_harvested_this_lap_mguh": "ers_harvested_this_lap_mguh",
            "ers_deployed_this_lap": "ers_deployed_this_lap",
        }

    @staticmethod
    def _get_enum_field_names():
        return {
            'traction_control': (TractionControl, 'traction_control'),
            'fuel_mix': (FuelMix, 'fuel_mix'),
            'actual_tyre_compound': (TyreCompound, 'actual_tyre_compound'),
            'visual_tyre_compound': (Tyre, 'visual_tyre_compound'),
            'vehicle_fia_flags': (Flag, 'vehicle_fia_flags'),
            'ers_deploy_mode': (ERSDeployMode, 'ers_deploy_mode'),
        }

    @staticmethod
    def _get_bool_field_names():
        return {
            'anti_lock_brakes_enabled': 'anti_lock_brakes',
            'pit_limiter_enabled': "pit_limiter_status",
            'drs_allowed': 'drs_allowed',
            'network_paused': 'network_paused',
        }

    def _primitive_value_changed(self, field, old_value, new_value):
        if field in (
            'ers_harvested_this_lap_mguk', 'ers_harvested_this_lap_mguh',
            'ers_deployed_this_lap', 'ers_store_energy',
            'drs_activation_distance', 'fuel_in_tank', 'fuel_capacity',
            'fuel_remaining_laps', 'max_rpm', 'idle_rpm', 'max_gears'
        ):
            return
        if field == 'tyres_age_laps':
            if new_value < old_value:
                self._log(f'Old tyres was {old_value} laps old and new one are {new_value} laps old.')
            return
        super(CarStatus, self)._primitive_value_changed(field, old_value, new_value)

    def _enum_value_changed(self, field, old_value, new_value):
        if field == 'ers_deploy_mode':
            ers_percent = round(100 * (self.ers_store_energy/ERS_CAPACITY_JOUL))
            if new_value == 'overtake':
                self._warn(f'Enabling overtake mode ! Available amount : {ers_percent}%')
            elif old_value == 'overtake':
                self._warn(f'Disabling overtake mode ! Remaining amount : {ers_percent}%')
            return
        if field == 'visual_tyre_compound':
            self._warn(f'Switching tyres from {old_value} to {new_value} !')
            return
        super(CarStatus, self)._enum_value_changed(field, old_value, new_value)

    def _bool_value_changed(self, field, new_value):
        if field != 'pit_limiter_enabled':
            return  # not needed to log this
        super(CarStatus, self)._bool_value_changed(field, new_value)
