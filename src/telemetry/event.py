from enum import Enum


class Event(Enum):
    SESSION_CREATED                    = 0
    SESSION_UPDATED                    = 1

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