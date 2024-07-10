from dataclasses import dataclass


@dataclass
class Motion:
    world_position_x: float = None
    world_position_y: float = None
    world_position_z: float = None
    world_velocity_x: float = None
    world_velocity_y: float = None
    world_velocity_z: float = None
    world_forward_dir_x: int = None
    world_forward_dir_y: int = None
    world_forward_dir_z: int = None
    world_right_dir_x: int = None
    world_right_dir_y: int = None
    world_right_dir_z: int = None
    g_force_lateral: float = None
    g_force_longitudinal: float = None
    g_force_vertical: float = None
    yaw: float = None
    pitch: float = None
    roll: float = None
