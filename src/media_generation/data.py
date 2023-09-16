from .models import *


# --- CIRCUITS

bahrein = Circuit(id='bahrein', name='Bahreïn', city='Sakhir', lap_length=5.412, best_lap="1' 31'' 447")
saudiarabia = Circuit(id='saudiarabia', name='Arabie Saoudite', city='Jeddah', lap_length=6.174, best_lap="1' 30'' 734")
australia = Circuit(id='australia', name='Australie', city='Melbourne', lap_length=5.278, best_lap="N/A")
imola = Circuit(id='imola', name='Imola', city='Imola', lap_length=4.909, best_lap="1' 15'' 484")
miami = Circuit(id='miami', name='Miami', city='Miami', lap_length=5.412, best_lap="1' 31'' 361")
spain = Circuit(id='spain', name='Espagne', city='Barcelona', lap_length=4.675, best_lap="1' 18'' 149")
monaco = Circuit(id='monaco', name='Monaco', city='Monaco', lap_length=3.337, best_lap="1' 12'' 909")
azerbaidjan = Circuit(id='azerbaidjan', name='Azerbaïdjan', city='Baku', lap_length=6.003, best_lap="1' 43'' 009")
canada = Circuit(id='canada', name='Canada', city='Montréal', lap_length=4.361, best_lap="1' 13'' 078")
gb = Circuit(id='gb', name='Grande-Bretagne', city='Silverstone', lap_length=5.891, best_lap="1' 27'' 097")
austria = Circuit(id='austria', name='Autriche', city='Spielberg', lap_length=4.318, best_lap="1' 05'' 619")
france = Circuit(id='france', name='France', city='Paul Ricard', lap_length=5.842, best_lap="1' 32'' 740")
hungary = Circuit(id='hungary', name='Hongrie', city='Budapest', lap_length=4.381, best_lap="1' 16'' 627")
belgium = Circuit(id='belgium', name='Belgique', city='Spa-Francorchamps', lap_length=7.004, best_lap="1' 41'' 252")
netherlands = Circuit(id='netherlands', name='Pays-Bas', city='Zandvoort', lap_length=4.259, best_lap="1' 11'' 097")
italy = Circuit(id='italy', name="Italie", city='Monza', lap_length=5.793, best_lap="1' 21'' 046")
singapore = Circuit(id='singapore', name='Singapour', city='Singapour', lap_length=5.063, best_lap="1' 41'' 905", fbrt_best_lap=BestLap(
                       pilot_name='FBRT_CiD16',
                       lap_time="1' 40'' 062",
                       season=1
                   ))
japan = Circuit(id='japan', name='Japon', city='Suzuka', lap_length=5.807, best_lap="1' 30'' 983")
austin = Circuit(id='austin', name='Etats-Unis', city='Austin', lap_length=5.513, best_lap="1' 36'' 169")
mexico = Circuit(id='mexico', name='Mexique', city='Mexico City', lap_length=4.304, best_lap="1' 17'' 774")
brazil = Circuit(id='brazil', name='Brésil', city='Sao Paulo', lap_length=4.309, best_lap="1' 10'' 540")
abudhabi = Circuit(id='abudhabi', name='Abu Dhabi', city='Yas Marina', lap_length=5.281, best_lap="1' 26'' 103")
portugal = Circuit(id='portugal', name='Portugal', city='Portimao', lap_length=4.653, best_lap="1' 18'' 750",
                   fbrt_best_lap=BestLap(
                       pilot_name='FBRT_Kayzor',
                       lap_time="1' 17'' 583",
                       season=4
                   ))
china = Circuit(id='china', name='Chine', city='Shanghai', lap_length=5.451, best_lap="1' 32'' 238")
qatar = Circuit(id='qatar', name='Qatar', city='Losail', lap_length=5.380, best_lap="1' 23'' 196")
lasvegas = Circuit(id='lasvegas', name='Las Vegas', city='Las Vegas', lap_length=6.120, best_lap="/")

circuits = {
    'Bahrein': bahrein,
    'Arabie Saoudite': saudiarabia,
    'Australie': australia,
    'Imola': imola,
    'Miami': miami,
    'Espagne': spain,
    'Monaco': monaco,
    'Azerbaïdjan': azerbaidjan,
    'Canada': canada,
    'Grande-Bretagne': gb,
    'Autriche': austria,
    'France': france,
    'Hongrie': hungary,
    'Belgique': belgium,
    'Pays-Bas': netherlands,
    'Italie': italy,
    'Singapour': singapore,
    'Japon': japan,
    'Etats-Unis': austin,
    'Mexique': mexico,
    'Brésil': brazil,
    'Abu Dhabi': abudhabi,
    'Portugal': portugal,
    'Chine': china,
    'Qatar': qatar,
    'Las Vegas': lasvegas,
}

# --- TEAMS

redbull = Team(
    name='RedBull',
    title='RED BULL',
    subtitle="Racing",
    main_color=(215, 190, 50),
    secondary_color=(0, 0, 186),
    box_color=(0, 0, 186),
    lineup_bg_color=(25, 18, 98),
    standing_bg=(22, 24, 95),
    standing_fg=(255, 255, 255),
    breaking_bg_color=(25, 26, 93),
    breaking_line_color=(15, 16, 83)
)
mercedes = Team(
    name='Mercedes',
    title='MERCEDES',
    subtitle="AMG Petronas F1 Team",
    main_color=(0, 179, 158),
    secondary_color=(0, 0, 0),
    box_color=(0, 179, 158),
    lineup_bg_color=(70, 161, 156),
    standing_bg=(0, 161, 156),
    standing_fg=(0, 0, 0),
    breaking_bg_color=(0, 210, 190),
    breaking_line_color=(0, 145, 130)
)
mclaren = Team(
    name='McLaren',
    title='McLAREN',
    subtitle='F1 Team',
    main_color=(224, 146, 12),
    secondary_color=(40, 40, 40),
    box_color=(224, 146, 12),
    lineup_bg_color=(239, 130, 1),
    standing_bg=(254, 128, 0),
    standing_fg=(255, 255, 255),
    breaking_bg_color=(255, 135, 0),
    breaking_line_color=(190, 80, 0),
    breaking_use_white_logo=True
)
haas = Team(
    name='Haas',
    title='HAAS',
    subtitle='F1 Team',
    main_color=(200, 10, 15),
    secondary_color=(211, 211, 211),
    box_color=(211, 211, 211),
    lineup_bg_color=(210, 7, 0),
    standing_bg=(255, 255, 255),
    standing_fg=(0, 0, 0),
    breaking_fg_color=(255, 255, 255),
    breaking_bg_color=(242, 23, 61),
    breaking_line_color=(178, 0, 23),
    breaking_use_white_logo=True,
    pole_fg_color=(0,0,0),
    pole_bg_color=(250, 250, 250),
    pole_line_color=(160, 160, 160)
)
alpine = Team(
    name='Alpine',
    title='ALPINE',
    subtitle='F1 Team',
    main_color=(10, 130, 210),
    secondary_color=(0, 0, 0),
    box_color=(9, 118, 193),
    lineup_bg_color=(13, 29, 44),
    standing_bg=(14, 28, 44),
    standing_fg=(255, 255, 255),
    breaking_bg_color=(20, 30, 40),
    breaking_line_color=(10, 20, 35),
    breaking_use_white_logo=True
)
ferrari = Team(
    name='Ferrari',
    title='FERRARI',
    subtitle='Scuderia',
    main_color=(255, 200, 200),
    secondary_color=(255, 0, 0),
    box_color=(167, 8, 6),
    lineup_bg_color=(234, 2, 0),
    standing_bg=(255, 0, 0),
    standing_fg=(0, 0, 0),
    breaking_bg_color=(255, 0, 0),
    breaking_line_color=(200, 0, 0)
)
williams = Team(
    name='Williams',
    title='WILLIAMS',
    subtitle="Racing",
    main_color=(6, 76, 187),
    secondary_color=(255, 255, 255),
    box_color=(6, 76, 187),
    lineup_bg_color=(13, 28, 67),
    standing_bg=(4, 30, 66),
    standing_fg=(255, 255, 255),
    breaking_bg_color=(6, 170, 230),
    breaking_line_color=(0, 110, 170),
    breaking_use_white_logo=True
)
alfa_romeo = Team(
    name='AlfaRomeo',
    title='ALFA ROMEO',
    subtitle='F1 Team ORLEN',
    main_color=(114, 4, 5),
    secondary_color=(255, 255, 255),
    box_color=(114, 4, 5),
    lineup_bg_color=(152, 13, 44),
    standing_bg=(153, 0, 0),
    standing_fg=(255, 255, 255),
    breaking_bg_color=(153, 0, 0),
    breaking_line_color=(120, 0, 0),
    breaking_use_white_logo=True
)
aston_martin = Team(
    name='AstonMartin',
    title='ASTON MARTIN',
    subtitle='Aramco Cognizant F1 Team',
    main_color=(14, 104, 88),
    secondary_color=(255, 255, 255),
    box_color=(14, 104, 88),
    lineup_bg_color=(36, 89, 79),
    standing_bg=(2, 87, 79),
    standing_fg=(255, 255, 255),
    breaking_bg_color=(2, 87, 79),
    breaking_line_color=(0, 60, 50)
)
alpha_tauri = Team(
    name="AlphaTauri",
    title="ALPHATAURI",
    subtitle='Scuderia',
    main_color=(40, 64, 90),
    secondary_color=(200, 200, 200),
    box_color=(40, 64, 90),
    lineup_bg_color=(15, 40, 71),
    standing_bg=(2, 41, 71),
    standing_fg=(255, 255, 255),
    breaking_bg_color=(35, 40, 80),
    breaking_line_color=(15, 20, 60),
    breaking_use_white_logo=True
)
DEFAULT_TEAM = Team(
    name='Default',
    title='Default',
    subtitle='Default',
    main_color=(0, 0, 0),
    secondary_color=(255, 0, 0),
    box_color=(186, 0, 0),
    lineup_bg_color=(186, 0, 0),
    standing_bg= (128,128,128),
    standing_fg = (255, 255, 255)
)
RESERVIST_TEAM = Team(
    name='Reservist',
    title='Reservist',
    subtitle='Reservist',
    main_color=(0, 0, 0),
    secondary_color=(200, 200, 200),
    box_color=(0, 0, 186),
    lineup_bg_color=(0, 0, 186),
    standing_bg= (128,128,128),
    standing_fg = (50,50,50)
)

teams_idx = {
    'RedBull': redbull,
    'Mercedes': mercedes,
    'McLaren': mclaren,
    'Haas': haas,
    'Alpine': alpine,
    'Ferrari': ferrari,
    'Williams': williams,
    'AlfaRomeo': alfa_romeo,
    'AstonMartin': aston_martin,
    'AlphaTauri': alpha_tauri
}

# --- DEFAULT TEAMS
teams = [
    redbull,
    mercedes,
    mclaren,
    haas,
    alpine,
    ferrari,
    williams,
    alfa_romeo,
    aston_martin,
    alpha_tauri
]