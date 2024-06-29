from dataclasses import dataclass

from src.telemetry.models.participant import Participant


@dataclass
class SpeedTrapEntry:
    participant: Participant
    participant_speed: float
    participant_is_fastest: bool
    speed_is_fastest_for_participant: bool
    fastest_speed_in_session: float
    fastest_participant: Participant
