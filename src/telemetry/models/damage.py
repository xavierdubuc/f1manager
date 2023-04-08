from dataclasses import dataclass
from typing import List


@dataclass
class Damage:
    tyres_wear: List[float] = None
    tyres_damage: List[int] = None
    brakes_damage: List[int] = None
    front_left_wing_damage: int = None
    front_right_wing_damage: int = None
    rear_wing_damage: int = None
    floor_damage: int = None
    diffuser_damage: int = None
    sidepod_damage: int = None
    drs_fault: bool = None
    ers_fault: bool = None
    gearbox_damage: int = None
    engined_damage: int = None
    engine_mguh_wear: int = None
    engine_energy_store_qear: int = None
    engine_control_electronics_wear: int = None
    engine_internal_combustion_engine_wear: int = None
    engine_mguk_wear: int = None
    engine_traction_control_wear: int = None
    engine_blown: bool = None
    engine_seized: bool = None
