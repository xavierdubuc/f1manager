from enum import Enum


class Event(Enum):
    SESSION_CREATED                   = 0
    SESSION_UPDATED                   = 1
    SESSION_ENDED                     = 2  # INCONSITENTLY FIRED

    PARTICIPANT_CREATED               = 10
    PARTICIPANT_LIST_INITIALIZED      = 11
    PARTICIPANT_UPDATED               = 12

    DAMAGE_CREATED                    = 20
    DAMAGE_LIST_INITIALIZED           = 21
    DAMAGE_UPDATED                    = 22

    TELEMETRY_CREATED                 = 30
    TELEMETRY_LIST_INITIALIZED        = 31
    TELEMETRY_UPDATED                 = 32

    CLASSIFICATION_CREATED            = 40
    CLASSIFICATION_LIST_INITIALIZED   = 41
    CLASSIFICATION_UPDATED            = 42

    LAP_RECORD_CREATED                = 50
    LAP_RECORD_UPDATED                = 51

    LAP_CREATED                       = 60
    LAP_UPDATED                       = 61
    LAP_START_CREATED                 = 62

    CAR_STATUS_CREATED                = 70
    CAR_STATUS_LIST_INITIALIZED       = 71
    CAR_STATUS_UPDATED                = 72

    CAR_SETUP_CREATED                 = 80
    CAR_SETUP_LIST_INITIALIZED        = 81
    CAR_SETUP_UPDATED                 = 82

    MOTION_CREATED                    = 90
    MOTION_LIST_INITIALIZED           = 91
    MOTION_UPDATED                    = 92

    TYRESET_CREATED                   = 100
    TYRESET_UPDATED                   = 101
    TYRESET_LIST_CREATED              = 102
    TYRESET_LIST_UPDATED              = 103

    FASTEST_LAP                       = 200
    COLLISION                         = 201
    OVERTAKE                          = 202
    SPEED_TRAP                        = 203

    BEST_SECTOR_UPDATED               = 500
