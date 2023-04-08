from enum import Enum


class GameMode(Enum):
    event_mode = 0
    grand_prix = 3
    time_trial = 5
    splitscreen = 6
    online_custom = 7
    online_league = 8
    career_invitational = 11
    championship_invitational = 12
    championship = 13
    online_championship = 14
    online_weekly_event = 15
    career_22 = 19
    career_22_online = 20
    benchmark = 127