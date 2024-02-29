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
    alfa_romeo=9
    my_team=41
    mercedes_2020=85
    ferrari_2020=86
    red_bull_2020=87
    williams_2020=88
    racing_point_2020=89
    renault_2020=90
    alpha_tauri_2020=91
    haas_2020=92
    mclaren_2020=93
    alfa_romeo_2020=94
    aston_martin_db11_v12=95
    aston_martin_vantage_f1_edition=96
    aston_martin_vantage_safety_car=97
    ferrari_f8_tributo=98
    ferrari_roma=99
    mclaren_720s=100
    mclaren_artura=101
    mercedes_amg_gt_black_series_safety_car=102
    mercedes_amg_gtr_pro=103
    f1_custom_team=104
    prema_21=106
    uni_virtuosi_21=107
    carlin_21=108
    hitech_21=109
    art_gp_21=110
    mp_motorsport_21=111
    charouz_21=112
    dams_21=113
    campos_21=114
    bwt_21=115
    trident_21=116
    mercedes_amg_gt_black_series=117
    mercedes_22=118
    ferrari_22=119
    red_bull_racing_22=120
    williams_22=121
    aston_martin_22=122
    alpine_22=123
    alpha_tauri_22=124
    haas_22=125
    mc_laren_22=126
    alfa_romeo_22=127
    konnersport_22=128
    konnersport=129
    prema_22=130
    virtuosi_22=131
    carlin_22=132
    mp_motorsport_22=133
    charouz_22=134
    dams_22=135
    campos_22=136
    van_amersfoort_racing_22=137
    trident_22=138
    hitech_22=139
    art_gp_22=140
    none=255

    def __str__(self) -> str:
        if self in (Team.mercedes, Team.mercedes_2020):
            return 'Mercedes'
        if self in (Team.ferrari, Team.ferrari_2020):
            return 'Ferrari'
        if self in (Team.red_bull_racing, Team.red_bull_2020):
            return 'Red Bull'
        if self in (Team.williams, Team.williams_2020):
            return 'Williams'
        if self in (Team.mclaren, Team.mclaren_2020):
            return 'McLaren'
        if self in (Team.haas, Team.haas_2020):
            return 'Haas'
        if self in (Team.alpha_tauri, Team.alpha_tauri_2020):
            return 'AlphaTauri'
        if self in (Team.alfa_romeo, Team.alfa_romeo_2020):
            return 'Alfa Romeo'
        if self in (Team.alpine, Team.renault_2020):
            return 'Alpine'
        if self in (Team.aston_martin, Team.racing_point_2020):
            return 'Aston Martin'
        return super().__str__()
