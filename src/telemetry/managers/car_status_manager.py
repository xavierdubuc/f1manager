from src.telemetry.models.car_status import CarStatus
from src.telemetry.models.enums.ers_deploy_mode import ERSDeployMode
from src.telemetry.models.enums.flag import Flag
from src.telemetry.models.enums.fuel_mix import FuelMix
from src.telemetry.models.enums.traction_control import TractionControl
from .abstract_manager import AbstractManager
from ..models.enums.tyre import Tyre

from ..models.enums.tyre_compound import TyreCompound


class CarStatusManager(AbstractManager):
    model = CarStatus

    primitive_fields = {
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

    enum_fields = {
        'traction_control': (TractionControl, 'traction_control'),
        'fuel_mix': (FuelMix, 'fuel_mix'),
        'actual_tyre_compound': (TyreCompound, 'actual_tyre_compound'),
        'visual_tyre_compound': (Tyre, 'visual_tyre_compound'),
        'vehicle_fia_flags': (Flag, 'vehicle_fia_flags'),
        'ers_deploy_mode': (ERSDeployMode, 'ers_deploy_mode'),
    }

    bool_fields = {
        'anti_lock_brakes_enabled': 'anti_lock_brakes',
        'pit_limiter_enabled': "pit_limiter_status",
        'drs_allowed': 'drs_allowed',
        'network_paused': 'network_paused',
    }
