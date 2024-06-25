from enum import Enum


class Team(Enum):
    mercedes=0
    ferrari=1
    red_bull_racing=2
    williams=3
    aston_martin=4
    alpine=5
    alpha_tauri=6
    haas=7
    mclaren=8
    kick_sauber=9
    my_team=41
    f1_custom_team=104
    art_gp_23=143
    campos_23=144
    carlin_23=145
    phm_23=146
    dams_23=147
    hitech_23=148
    mp_motorsport_23=149
    prema_23=150
    trident_23=151
    van_amersfoort_racing_23=152
    virtuosi_23=153
    none=255

    def __str__(self) -> str:
        if self == Team.mercedes:
            return 'Mercedes'
        if self == Team.ferrari:
            return 'Ferrari'
        if self == Team.red_bull_racing:
            return 'RedBull'
        if self == Team.williams:
            return 'Williams'
        if self == Team.mclaren:
            return 'McLaren'
        if self == Team.haas:
            return 'Haas'
        if self == Team.alpha_tauri:
            return 'AlphaTauri'
        if self == Team.kick_sauber:
            return 'KickSauber'
        if self == Team.alpine:
            return 'Alpine'
        if self == Team.aston_martin:
            return 'AstonMartin'
        return super().__str__()

    def as_emoji(self):
        return str(self).lower()
