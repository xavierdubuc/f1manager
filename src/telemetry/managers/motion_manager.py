from ..models.motion import Motion
from .abstract_manager import AbstractManager


class MotionManager(AbstractManager):
    model = Motion

    primitive_fields = {
        'world_position_x': 'world_position_x',
        'world_position_y': 'world_position_y',
        'world_position_z': 'world_position_z',
        'world_velocity_x': 'world_velocity_x',
        'world_velocity_y': 'world_velocity_y',
        'world_velocity_z': 'world_velocity_z',
        'world_forward_dir_x': 'world_forward_dir_x',
        'world_forward_dir_y': 'world_forward_dir_y',
        'world_forward_dir_z': 'world_forward_dir_z',
        'world_right_dir_x': 'world_right_dir_x',
        'world_right_dir_y': 'world_right_dir_y',
        'world_right_dir_z': 'world_right_dir_z',
        'g_force_lateral': 'g_force_lateral',
        'g_force_longitudinal': 'g_force_longitudinal',
        'g_force_vertical': 'g_force_vertical',
        'yaw': 'yaw',
        'pitch': 'pitch',
        'roll': 'roll',
    }

    enum_fields = {}

    bool_fields = {}
