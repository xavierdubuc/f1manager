from src.telemetry.models.tyreset import TyreSet
from src.telemetry.models.enums.session_type import SessionType
from src.telemetry.models.enums.tyre import Tyre
from src.telemetry.models.enums.tyre_compound import TyreCompound
from .abstract_manager import AbstractManager


class TyreSetManager(AbstractManager):
    model = TyreSet

    primitive_fields = {
        'wear': 'wear',
        'life_span': 'life_span',
        'usable_life': 'usable_life',
        'lap_delta_time': 'lap_delta_time',
    }

    enum_fields = {
        'actual_tyre_compound': (TyreCompound, 'actual_tyre_compound'),
        'visual_tyre_compound': (Tyre, 'visual_tyre_compound'),
        'recommended_session': (SessionType, 'recommended_session'),
    }

    bool_fields = {
        'available': 'available',
        'fitted': 'fitted'
    }
