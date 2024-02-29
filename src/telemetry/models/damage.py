from dataclasses import dataclass
from typing import List


@dataclass
class Damage:
    tyres_wear: List[float] = None
    tyres_damage: List[int] = None # RL RR FL FR
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
    engine_energy_store_wear: int = None
    engine_control_electronics_wear: int = None
    engine_internal_combustion_engine_wear: int = None
    engine_mguk_wear: int = None
    engine_turbo_charger_wear: int = None
    engine_blown: bool = None
    engine_seized: bool = None

    def has_broken_tyre(self) -> str:
        return 100 in self.tyres_damage

    def get_current_status(self) -> str:
        # CAR chassis damages
        damage_keys = {
            'front_left_wing_damage':  'Aileron avant gauche',
            'front_right_wing_damage': 'Aileron avant droit',
            'rear_wing_damage':        'Aileron arrière',
            'floor_damage':            'Fond plat',
            'diffuser_damage':         'Diffuseur',
            'sidepod_damage':          'Sidepods',
        }
        statuses = []
        max_damage_area_label_size = max([len(v) for v in damage_keys.values()])

        for key, text in damage_keys.items():
            label = text.rjust(max_damage_area_label_size)
            damage_value = getattr(self, key)
            circle = self.get_component_status(damage_value)
            damage_value_str = f'{str(damage_value).rjust(3)} %'
            statuses.append(
                f"> `{label}: {damage_value_str}`  {circle}"
            )

        # TYRE damages
        # 100% 🔴 ━━━━ 🟡  45%
        # 56% 🟠 ━━━━ 🟢   32% 


        front_left = f'`{str(self.tyres_damage[2]).rjust(3)} %`  {self.get_component_status(self.tyres_damage[2], "🛞")}'
        front_right = f'{self.get_component_status(self.tyres_damage[3], "🛞")}  `{str(self.tyres_damage[3]).rjust(3)} %`'
        rear_left = f'`{str(self.tyres_damage[0]).rjust(3)} %`  {self.get_component_status(self.tyres_damage[0], "🛞")}'
        rear_right = f'{self.get_component_status(self.tyres_damage[1], "🛞")}  `{str(self.tyres_damage[1]).rjust(3)} %`'
        statuses += [
            f'{front_left} ━━━━ {front_right}',
            ''
            f'{rear_left} ━━━━ {rear_right}',
        ]
        return '\n'.join(statuses)

    def get_component_status(self, value, no_damage_icon=''):
        if value >= 75:
            return '🔴'
        if value >= 50:
            return '🟠'
        if value >= 10:
            return '🟡'
        if value > 0:
            return '🟢'
        return no_damage_icon

    def get_component_color(self, value):
        if value >= 75:
            return 'red'
        if value >= 50:
            return 'orange'
        if value >= 15:
            return 'yellow'
        if value > 0:
            return 'lightgreen'
        return 'green'

    def get_front_left_tyre_damage_value(self):
        return self.tyres_damage[2]

    def get_front_right_tyre_damage_value(self):
        return self.tyres_damage[3]

    def get_rear_left_tyre_damage_value(self):
        return self.tyres_damage[0]

    def get_rear_right_tyre_damage_value(self):
        return self.tyres_damage[1]

    def get_max_tyre_damage(self):
        return max(self.tyres_damage)

    def get_mean_tyre_damage(self):
        return round(sum(self.tyres_damage) / 4)
