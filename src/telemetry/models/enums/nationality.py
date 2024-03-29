from enum import Enum


class Nationality(Enum):
    none = 0
    american = 1
    argentinean = 2
    australian = 3
    austrian = 4
    azerbaijan = 5
    bahraini = 6
    belgian = 7
    bolivian = 8
    brazilian = 9
    british = 10
    bulgarian = 11
    cameroonian = 12
    canadian = 13
    chilean = 14
    chinese = 15
    colombian = 16
    costa_rican = 17
    croatian = 18
    cypriot = 19
    czech = 20
    danish = 21
    dutch = 22
    ecuadorian = 23
    english = 24
    emirian = 25
    estonian = 26
    finnish = 27
    french = 28
    german = 29
    ghanaian = 30
    greek = 31
    guatemalan = 32
    honduran = 33
    hong_konger = 34
    hungarian = 35
    icelander = 36
    indian = 37
    indonesian = 38
    irish = 39
    israeli = 40
    italian = 41
    jamaican = 42
    japanese = 43
    jordanian = 44
    kuwaiti = 45
    latvian = 46
    lebanese = 47
    lithuanian = 48
    luxembourger = 49
    malaysian = 50
    maltese = 51
    mexican = 52
    monegasque = 53
    new_zealander = 54
    nicaraguan = 55
    northern_irish = 56
    norwegian = 57
    omani = 58
    pakistani = 59
    panamanian = 60
    paraguayan = 61
    peruvian = 62
    polish = 63
    portuguese = 64
    qatari = 65
    romanian = 66
    russian = 67
    salvadoran = 68
    saudi = 69
    scottish = 70
    serbian = 71
    singaporean = 72
    slovakian = 73
    slovenian = 74
    south_korean = 75
    south_african = 76
    spanish = 77
    swedish = 78
    swiss = 79
    thai = 80
    turkish = 81
    uruguayan = 82
    ukrainian = 83
    venezuelan = 84
    barbadian = 85
    welsh = 86
    vietnamese = 87
    algerian=88
    not_defined=255

    def __str__(self):
        if self == Nationality.belgian:
            return '🇧🇪'
        if self == Nationality.french:
            return '🇫🇷'
        if self == Nationality.italian:
            return '🇮🇹'
        return super().__str__()