from typing import Dict
from src.telemetry.event import Event

from src.telemetry.managers.abstract_manager import Change
from src.telemetry.models.damage import Damage
from src.telemetry.models.enums.result_status import ResultStatus
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session
from .abstract_listener import AbstractListener

class NoticeableDamageListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.DAMAGE_UPDATED
    ]

    def _on_damage_updated(self, damage:Damage, changes:Dict[str, Change], participant:Participant, session:Session) -> str:
        # don't mention anything about not running pilots
        if session.get_participant_status(participant) not in (ResultStatus.active, ResultStatus.invalid, ResultStatus.inactive):
            return
        if not self._has_noticeable_damage_changes(changes):
            return
        main_msg = f'**{participant}** → {self._get_changes_description(changes)}'
        car_status = damage.get_current_status()
        msg = '\n'.join([main_msg, car_status])
        return msg

    def _has_noticeable_damage_changes(self, changes:Dict[str, Change]) -> bool:
        if not changes:
            return False

        damage_keys = [
            'front_left_wing_damage' ,
            'front_right_wing_damage',
            'rear_wing_damage'       ,
            'floor_damage'           ,
            'diffuser_damage'        ,
            'sidepod_damage'         ,
        ]
        has_damage_changes = any(key in changes for key in damage_keys)
        if has_damage_changes:
            return True

        tyre_damages = changes.get('tyres_damage')
        if tyre_damages and 100 in tyre_damages.actual:
            return True

        return False

    def _get_changes_description(self, changes:Dict[str, Change]) -> str:
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
                changed_parts.append(f'{text} {self._get_component_status(actual_value)}')

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

    def _get_component_status(self, value):
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