# --- CIRCUITS

from src.media_generation.models.circuit import Circuit
from src.media_generation.models.team import Team


bahrein = Circuit(id='bahrein', name='Bahreïn', city='Sakhir', lap_length=5.412, best_lap="1' 31'' 447", emoji='🇧🇭')
saudiarabia = Circuit(id='saudiarabia', name='Arabie Saoudite', city='Jeddah', lap_length=6.174, best_lap="1' 30'' 734", emoji='🇸🇦')
australia = Circuit(id='australia', name='Australie', city='Melbourne', lap_length=5.278, best_lap="N/A", emoji='🇦🇺')
imola = Circuit(id='imola', name='Imola', city='Imola', lap_length=4.909, best_lap="1' 15'' 484", emoji='🇮🇹')
miami = Circuit(id='miami', name='Miami', city='Miami', lap_length=5.412, best_lap="1' 31'' 361", emoji='🇺🇸')
spain = Circuit(id='spain', name='Espagne', city='Barcelona', lap_length=4.675, best_lap="1' 18'' 149", emoji='🇪🇸')
monaco = Circuit(id='monaco', name='Monaco', city='Monaco', lap_length=3.337, best_lap="1' 12'' 909", emoji='🇲🇨')
azerbaidjan = Circuit(id='azerbaidjan', name='Azerbaïdjan', city='Baku', lap_length=6.003, best_lap="1' 43'' 009", emoji='🇦🇿')
canada = Circuit(id='canada', name='Canada', city='Montréal', lap_length=4.361, best_lap="1' 13'' 078", emoji='🇨🇦')
gb = Circuit(id='gb', name='Grande-Bretagne', city='Silverstone', lap_length=5.891, best_lap="1' 27'' 097", emoji='🇬🇧')
austria = Circuit(id='austria', name='Autriche', city='Spielberg', lap_length=4.318, best_lap="1' 05'' 619", emoji='🇦🇹')
france = Circuit(id='france', name='France', city='Paul Ricard', lap_length=5.842, best_lap="1' 32'' 740", emoji='🇫🇷')
hungary = Circuit(id='hungary', name='Hongrie', city='Budapest', lap_length=4.381, best_lap="1' 16'' 627", emoji='🇭🇺')
belgium = Circuit(id='belgium', name='Belgique', city='Spa-Francorchamps', lap_length=7.004, best_lap="1' 41'' 252", emoji='🇧🇪')
netherlands = Circuit(id='netherlands', name='Pays-Bas', city='Zandvoort', lap_length=4.259, best_lap="1' 11'' 097", emoji='🇳🇱')
italy = Circuit(id='italy', name="Italie", city='Monza', lap_length=5.793, best_lap="1' 21'' 046", emoji='🇮🇹')
singapore = Circuit(id='singapore', name='Singapour', city='Singapour', lap_length=5.063, best_lap="1' 41'' 905", emoji='🇸🇬')
japan = Circuit(id='japan', name='Japon', city='Suzuka', lap_length=5.807, best_lap="1' 30'' 983", emoji='🇯🇵')
austin = Circuit(id='austin', name='Etats-Unis', city='Austin', lap_length=5.513, best_lap="1' 36'' 169", emoji='🇺🇸')
mexico = Circuit(id='mexico', name='Mexique', city='Mexico City', lap_length=4.304, best_lap="1' 17'' 774", emoji='🇲🇽')
brazil = Circuit(id='brazil', name='Brésil', city='Sao Paulo', lap_length=4.309, best_lap="1' 10'' 540", emoji='🇧🇷')
abudhabi = Circuit(id='abudhabi', name='Abu Dhabi', city='Yas Marina', lap_length=5.281, best_lap="1' 26'' 103", emoji='🇦🇪')
portugal = Circuit(id='portugal', name='Portugal', city='Portimao', lap_length=4.653, best_lap="1' 18'' 750", emoji='🇵🇹')
china = Circuit(id='china', name='Chine', city='Shanghai', lap_length=5.451, best_lap="1' 32'' 238", emoji='🇨🇳')
qatar = Circuit(id='qatar', name='Qatar', city='Losail', lap_length=5.380, best_lap="1' 23'' 196", emoji='🇶🇦')
lasvegas = Circuit(id='lasvegas', name='Las Vegas', city='Las Vegas', lap_length=6.120, best_lap="/", emoji='🇺🇸')

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
    title='RED BULL RACING',
    display_name="RED BULL RACING",
    psd_name="redbull",
    main_color=(215, 190, 50),
    secondary_color=(0, 0, 186),
    box_color=(0, 0, 186),
    lineup_bg_color=(22, 25, 96),
    standing_bg=(22, 24, 95),
    standing_fg=(255, 255, 255),
    transparent_color=(120, 130, 200),
    breaking_bg_color=(25, 26, 93),
    breaking_line_color=(15, 16, 83),
    alternate_main_color=(0,0,186),
    driver_of_the_day_hsv_offset=150,
    driver_of_the_day_use_grayscale=False,
)
mercedes = Team(
    name='Mercedes',
    title='MERCEDES',
    display_name="MERCEDES",
    psd_name="mercedes",
    main_color=(0, 179, 158),
    secondary_color=(0, 0, 0),
    box_color=(0, 179, 158),
    lineup_bg_color=(70, 161, 154),
    lineup_fg_color=(0, 0, 0),
    standing_bg=(0, 245, 211),
    standing_fg=(0, 0, 0),
    transparent_color=(120, 200, 195),
    breaking_bg_color=(0, 210, 190),
    breaking_line_color=(0, 145, 130),
    driver_of_the_day_hsv_offset=120,
    driver_of_the_day_use_grayscale=False,
)
mclaren = Team(
    name='McLaren',
    title='McLAREN',
    display_name='McLAREN',
    psd_name="mclaren",
    main_color=(224, 146, 12),
    secondary_color=(40, 40, 40),
    box_color=(224, 146, 12),
    lineup_bg_color=(240, 127, 5),
    standing_bg=(254, 128, 0),
    standing_fg=(255, 255, 255),
    transparent_color=(255, 155, 55),
    breaking_bg_color=(255, 135, 0),
    breaking_line_color=(190, 80, 0),
    breaking_use_white_logo=True,
    driver_of_the_day_hsv_offset=25,
    driver_of_the_day_use_grayscale=False,
)
haas = Team(
    name='Haas',
    title='HAAS',
    display_name='HAAS',
    psd_name="haas",
    main_color=(200, 10, 15),
    secondary_color=(211, 211, 211),
    box_color=(211, 211, 211),
    lineup_bg_color=(228, 6, 19),
    standing_bg=(255, 255, 255),
    standing_fg=(0, 0, 0),
    transparent_color=(240, 240, 240),
    breaking_fg_color=(255, 255, 255),
    breaking_bg_color=(242, 23, 61),
    breaking_line_color=(178, 0, 23),
    breaking_use_white_logo=True,
    pole_fg_color=(0,0,0),
    pole_bg_color=(250, 250, 250),
    pole_line_color=(160, 160, 160),
    driver_of_the_day_hsv_offset=5,
    driver_of_the_day_use_grayscale=True,
)
alpine = Team(
    name='Alpine',
    title='ALPINE',
    display_name='ALPINE',
    psd_name="alpine",
    main_color=(10, 130, 210),
    secondary_color=(0, 0, 0),
    box_color=(9, 118, 193),
    lineup_bg_color=(12, 29, 45),
    lineup_fg_color=(53, 116, 209),
    standing_bg=(14, 28, 44),
    standing_fg=(255, 255, 255),
    transparent_color=(45, 90, 140),
    breaking_bg_color=(20, 30, 40),
    breaking_line_color=(10, 20, 35),
    alternate_main_color=(9, 118, 193),
    breaking_use_white_logo=True,
    driver_of_the_day_hsv_offset=170,
    driver_of_the_day_use_grayscale=False,
)
ferrari = Team(
    name='Ferrari',
    title='FERRARI',
    display_name='FERRARI',
    psd_name="ferrari",
    main_color=(255, 200, 200),
    secondary_color=(255, 0, 0),
    box_color=(167, 8, 6),
    lineup_bg_color=(234, 1, 7),
    standing_bg=(255, 0, 0),
    standing_fg=(0, 0, 0),
    transparent_color=(255,125,125),
    breaking_bg_color=(255, 0, 0),
    breaking_line_color=(200, 0, 0),
    driver_of_the_day_hsv_offset=5,
    driver_of_the_day_use_grayscale=False,
)
williams = Team(
    name='Williams',
    title='WILLIAMS',
    display_name="WILLIAMS",
    psd_name="williams",
    main_color=(6, 76, 187),
    secondary_color=(255, 255, 255),
    box_color=(6, 76, 187),
    lineup_bg_color=(10, 26, 85),
    lineup_fg_color=(61, 162, 221),
    standing_bg=(0,0, 254),
    standing_fg=(255, 255, 255),
    transparent_color=(120, 160, 195),
    breaking_bg_color=(6, 170, 230),
    breaking_line_color=(0, 110, 170),
    alternate_main_color=(7,48,102),
    breaking_use_white_logo=True,
    driver_of_the_day_hsv_offset=160,
    driver_of_the_day_use_grayscale=False,
)
aston_martin = Team(
    name='AstonMartin',
    title='ASTON MARTIN',
    display_name='ASTON MARTIN',
    psd_name="aston",
    main_color=(14, 104, 88),
    alternate_main_color=(3, 115, 100),
    secondary_color=(255, 255, 255),
    box_color=(14, 104, 88),
    lineup_bg_color=(37, 88, 79),
    standing_bg=(2, 87, 79),
    standing_fg=(255, 255, 255),
    transparent_color=(100, 175, 110),
    breaking_bg_color=(2, 87, 79),
    breaking_line_color=(0, 60, 50),
    driver_of_the_day_hsv_offset=100,
    driver_of_the_day_use_grayscale=False,
)
# F1 < 2024
alfa_romeo = Team(
    name='AlfaRomeo',
    title='ALFA ROMEO',
    display_name='ALFA ROMEO',
    main_color=(114, 4, 5),
    secondary_color=(255, 255, 255),
    box_color=(114, 4, 5),
    lineup_bg_color=(152, 13, 44),
    standing_bg=(153, 0, 0),
    standing_fg=(255, 255, 255),
    transparent_color=(200,120,120),
    breaking_bg_color=(153, 0, 0),
    breaking_line_color=(120, 0, 0),
    breaking_use_white_logo=True,
    driver_of_the_day_hsv_offset=250,
    driver_of_the_day_use_grayscale=False,
)
alpha_tauri = Team(
    name="AlphaTauri",
    title="ALPHATAURI",
    display_name='ALPHA TAURI',
    main_color=(40, 64, 90),
    secondary_color=(200, 200, 200),
    box_color=(40, 64, 90),
    lineup_bg_color=(15, 40, 71),
    standing_bg=(2, 41, 71),
    standing_fg=(255, 255, 255),
    transparent_color=(81, 135, 175),
    breaking_bg_color=(35, 40, 80),
    breaking_line_color=(15, 20, 60),
    alternate_main_color=(40, 64, 90),
    breaking_use_white_logo=True,
    driver_of_the_day_hsv_offset=140,
    driver_of_the_day_use_grayscale=False,
)
# F1 >= 2024
kick_sauber = Team(
    name='KickSauber',
    title='KICK SAUBER',
    display_name='KICK SAUBER',
    psd_name="kick",
    main_color=(0, 255, 0),
    secondary_color=(0,0,0),
    box_color=(114, 4, 5),
    lineup_bg_color=(0, 0, 0),
    lineup_fg_color=(94, 236, 0),
    standing_bg=(0, 231, 1),
    standing_fg=(0,0,0),
    transparent_color=(200,120,120),
    breaking_bg_color=(153, 0, 0),
    breaking_line_color=(120, 0, 0),
    breaking_use_white_logo=False,
    driver_of_the_day_hsv_offset=90,
    driver_of_the_day_use_grayscale=False,
)
vcarb = Team(
    name="VCARB",
    title="RB",
    display_name='RB',
    psd_name="visa",
    standing_bg=(20, 52, 203),
    main_color=(40, 64, 90),
    secondary_color=(200, 200, 200),
    box_color=(40, 64, 90),
    lineup_bg_color=(35, 37, 208),
    standing_fg=(255, 255, 255),
    transparent_color=(81, 135, 175),
    breaking_bg_color=(35, 40, 80),
    breaking_line_color=(15, 20, 60),
    alternate_main_color=(40, 64, 90),
    breaking_use_white_logo=False,
    driver_of_the_day_hsv_offset=140,
    driver_of_the_day_use_grayscale=False,
)

# DEFAULTS

DEFAULT_TEAM = Team(
    name='Default',
    title='Default',
    display_name='DEFAULT',
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
    display_name='RESERVIST',
    main_color=(0, 0, 0),
    secondary_color=(200, 200, 200),
    box_color=(0, 0, 186),
    lineup_bg_color=(0, 0, 186),
    standing_bg= (128,128,128),
    standing_fg = (50,50,50)
)
ASPIRANT_TEAM = Team(
    name='Aspirant',
    title='Aspirant',
    display_name='ASPIRANT',
    main_color=(0, 0, 0),
    secondary_color=(200, 200, 200),
    box_color=(0, 0, 186),
    lineup_bg_color=(0, 0, 186),
    standing_bg= (255, 255, 255),
    standing_fg = (0,0,0)
)

teams_idx = {
    'RedBull': redbull,
    'Mercedes': mercedes,
    'McLaren': mclaren,
    'Haas': haas,
    'Alpine': alpine,
    'Ferrari': ferrari,
    'Williams': williams,
    'AstonMartin': aston_martin,
    'VCARB': vcarb,
    'KickSauber': kick_sauber,
    'AlfaRomeo': alfa_romeo,
    'AlphaTauri': alpha_tauri,
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
    alpha_tauri,
    vcarb,
    kick_sauber
]
