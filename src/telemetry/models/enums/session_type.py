from enum import Enum


class SessionType(Enum):
    unknown = 0
    fp1 = 1
    fp2 = 2
    fp3 = 3
    short_p = 4
    q1 = 5
    q2 = 6
    q3 = 7
    short_q = 8
    one_lap_q = 9
    sprint_q1 = 10
    sprint_q2 = 11
    sprint_q3 = 12
    sprint_short_q = 13
    sprint_one_shot = 14
    race = 15
    race2 = 16
    race3 = 17
    clm = 18

    def __str__(self):
        if self == SessionType.race:
            return "Course"
        if self == SessionType.race_2:
            return "Course 2"
        if self == SessionType.race_3:
            return "Course 3"
        if self == SessionType.short_p:
            return "Essais courts"
        if self == SessionType.short_q:
            return "Qualifs courtes"
        if self == SessionType.one_lap_q:
            return "Qualif en un tour"
        if self == SessionType.clm:
            return "Contre-la-montre"
        return self.name.capitalize()

    def is_race(self):
        return self in (
            SessionType.race, SessionType.race_2, SessionType.race_3
        )

    def is_clm(self):
        return self == SessionType.clm

    def is_qualification(self):
        return self in (
            SessionType.one_lap_q, SessionType.q1, SessionType.q2,
            SessionType.q3, SessionType.short_q
        )
