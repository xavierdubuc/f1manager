from typing import Dict
from .abstract_manager import AbstractManager, Change
from ..models.damage import Damage
from f1_22_telemetry.packets import CarDamageData


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
        'engine_energy_store_qear': 'engine_energy_store_qear',
        'engine_control_electronics_wear': 'engine_control_electronics_wear',
        'engine_internal_combustion_engine_wear': 'engine_internal_combustion_engine_wear',
        'engine_mguk_wear': 'engine_mguk_wear',
        'engine_traction_control_wear': 'engine_traction_control_wear',
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

    @classmethod
    def has_noticeable_damage_changes(cls, changes:dict):
        if not changes:
            return False

        damage_keys = [
            'front_left_wing_damage',
            'front_right_wing_damage',
            'rear_wing_damage',
            'floor_damage',
            'diffuser_damage',
            'sidepod_damage',
        ]
        has_damage_changes = any(key in changes for key in damage_keys)
        if has_damage_changes:
            return True

        tyre_damages = changes.get('tyres_damage')
        if tyre_damages and 100 in tyre_damages.actual:
            return True

        return False

    @classmethod
    def get_changes_description(cls, changes:dict) -> str:
        # if broken tyre
        tyre_damage_change = changes.get('tyres_damage')
        if tyre_damage_change and 100 in tyre_damage_change.actual:
            tyre_damage = tyre_damage_change.actual
            if tyre_damage[0] == 100:
                pos = 'arrière gauche'
            elif tyre_damage[1] == 100:
                pos = 'arrière droite'
            elif tyre_damage[2] == 100:
                pos = 'avant gauche'
            else:
                pos = 'avant droite'
            return f'🔴 🛞 Crevaison ou roue {pos} arrachée !'

        damage_keys = {
            'front_left_wing_damage':  'Aileron avant gauche',
            'front_right_wing_damage': 'Aileron avant droit',
            'rear_wing_damage':        'Aileron arrière',
            'floor_damage':            'Fond plat',
            'diffuser_damage':         'Diffuseur',
            'sidepod_damage':          'Sidepods',
        }
        is_increase = False
        is_decrease = False

        changed_parts = []
        for key, text in damage_keys.items():
            if key in changes:
                actual_value = changes[key].actual
                changed_parts.append(f'{text} {cls.get_component_status(actual_value)}')

                # detect if overall there has been only decrease or increase values or both
                # to determine the verb to use in the message
                if changes[key].old < actual_value:
                    is_increase = True
                else:
                    is_decrease = True

        verb_parts = [
            'subis' if is_increase else '',
            "/" if is_increase and is_decrease else '',
            'réparés' if is_decrease else ''
        ]
        verb = "".join(verb_parts)
        return f'Dégats {verb} sur : {", ".join(changed_parts)}'

    @classmethod
    def get_component_status(cls, value):
        if value >= 75:
            circle = '🔴'
        elif value >= 50:
            circle = '🟠'
        elif value >= 10:
            circle = '🟡'
        elif value > 0:
            circle = '🟢'
        else:
            circle = ' '
        return f'{circle} ({str(value).rjust(3)}%)'