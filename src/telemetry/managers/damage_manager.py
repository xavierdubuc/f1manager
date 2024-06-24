from typing import Dict
from .abstract_manager import AbstractManager, Change
from ..models.damage import Damage
from f1_24_telemetry.packets import CarDamageData


class DamageManager(AbstractManager):
    model = Damage

    primitive_fields = {
        'front_left_wing_damage': 'front_left_wing_damage',
        'front_right_wing_damage': 'front_right_wing_damage',
        'rear_wing_damage': 'rear_wing_damage',
        'floor_damage': 'floor_damage',
        'diffuser_damage': 'diffuser_damage',
        'sidepod_damage': 'sidepod_damage',
        'gearbox_damage': 'gearbox_damage',
        'engined_damage': 'engined_damage',
        'engine_mguh_wear': 'engine_mguh_wear',
        'engine_energy_store_wear': 'engine_energy_store_wear',
        'engine_control_electronics_wear': 'engine_control_electronics_wear',
        'engine_internal_combustion_engine_wear': 'engine_internal_combustion_engine_wear',
        'engine_mguk_wear': 'engine_mguk_wear',
        'engine_turbo_charger_wear': 'engine_turbo_charger_wear',
    }

    enum_fields = {}

    bool_fields = {
        'drs_fault': 'drs_fault',
        'ers_fault': 'ers_fault',
        'engine_blown': 'engine_blown',
        'engine_seized': 'engine_seized',
    }

    @classmethod
    def create(cls, packet: CarDamageData) -> Damage:
        self = super().create(packet)
        self.tyres_wear = list(packet.tyres_wear)
        return self

    @classmethod
    def update(cls, damage:Damage, packet: CarDamageData) -> Dict[str, Change]:
        changes = super().update(damage, packet)

        # TODO refactor put this logic in parent
        list_fields = [
            'tyres_wear',
            'tyres_damage',
            'brakes_damage'
        ]
        for field in list_fields:
            new_value = list(getattr(packet, field))
            old_value = getattr(damage, field)
            if new_value != old_value:
                changes[field]= Change(actual=new_value, old=old_value)
                setattr(damage, field, new_value)

        return changes
