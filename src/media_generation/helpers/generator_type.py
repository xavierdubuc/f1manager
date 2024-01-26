import enum

class GeneratorType(enum.Enum):
    # RACE
    PRESENTATION = 'presentation'
    LINEUP ='lineups'
    POLE = 'pole'
    GRID_VID = 'grid_ribbon'
    GRID = 'grid'
    RESULTS = 'results'
    DRIVER_OF_THE_DAY = 'driver_of_the_day'

    # GENERAL
    TEAMS_RANKING = 'teams_ranking'
    PILOTS_RANKING = 'pilots_ranking'
    LICENSE_POINTS = 'license_points'

    # MULTIPLE SHEETS
    CALENDAR = 'calendar'
    SEASON_RANKING = 'season_ranking'

    # _values SHEET
    NUMBERS = 'numbers'
    PILOT = 'pilot'
    SEASON_LINEUP = 'season_lineup'
