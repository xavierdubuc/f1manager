from enum import Enum


class Track(Enum):
    unknown = -1
    melbourne = 0
    paul_ricard = 1
    shanghai = 2
    bahrain = 3
    catalunya = 4
    monaco = 5
    montreal = 6
    silverstone = 7
    hockenheim = 8
    hungaroring = 9
    spa = 10
    monza = 11
    singapore = 12
    suzuka = 13
    abudhabi = 14
    texas = 15
    brazil = 16
    austria = 17
    sochi = 18
    mexico = 19
    baku = 20
    bahrain_short = 21
    silverstone_short = 22
    texas_short = 23
    suzuka_short = 24
    hanoi = 25
    zandvoort = 26
    imola = 27
    portimão = 28
    jeddah = 29
    miami = 30
    las_vegas = 31
    qatar = 32

    def __str__(self):
        return self.name.replace('_', ' ').capitalize()

    def get_name(self):
        if self == Track.melbourne:
            return 'Australie'
        if self == Track.paul_ricard:
            return 'France'
        if self == Track.shanghai:
            return 'Chine'
        if self == Track.bahrain:
            return 'Bahrein'
        if self == Track.catalunya:
            return 'Espagnne'
        if self == Track.monaco:
            return 'Monaco'
        if self == Track.montreal:
            return 'Canada'
        if self == Track.silverstone:
            return 'Grande-Bretagne'
        if self == Track.hungaroring:
            return 'Hongrie'
        if self == Track.spa:
            return 'Belgique'
        if self == Track.monza:
            return 'Italie'
        if self == Track.singapore:
            return 'Singapour'
        if self == Track.suzuka:
            return 'Japon'
        if self == Track.abudhabi:
            return 'Abu Dhabi'
        if self == Track.texas:
            return 'Etats-Unis'
        if self == Track.brazil:
            return 'Brésil'
        if self == Track.austria:
            return 'Autriche'
        if self == Track.mexico:
            return 'Mexique'
        if self == Track.baku:
            return 'Azerbaïdjan'
        if self == Track.zandvoort:
            return 'Pays-Bas'
        if self == Track.imola:
            return 'Imola'
        if self == Track.portimão:
            return 'Portugal'
        if self == Track.jeddah:
            return 'Arabie Saoudite'
        if self == Track.miami:
            return 'Miami'
        if self == Track.las_vegas:
            return 'Las Vegas'
        if self == Track.qatar:
            return 'Qatar'
        return 'Unknown'
