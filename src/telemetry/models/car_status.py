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
from src.telemetry.models.participant import Participant

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