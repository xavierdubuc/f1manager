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

    @property
    def participant_speed_as_int(self):
        return int(self.participant_speed)

    def __eq__(self, other:"SpeedTrapEntry"):
        return self.participant_speed_as_int == other.participant_speed_as_int

    def __lt__(self, other:"SpeedTrapEntry"):
        return self.participant_speed_as_int < other.participant_speed_as_int

    def __gt__(self, other:"SpeedTrapEntry"):
        return self.participant_speed_as_int > other.participant_speed_as_int

    def __ge__(self, other:"SpeedTrapEntry"):
        return self.participant_speed_as_int >= other.participant_speed_as_int

    def __le__(self, other:"SpeedTrapEntry"):
        return self.participant_speed_as_int <= other.participant_speed_as_int

    def __str__(self):
        return f'{self.participant} : {self.participant_speed_as_int} KM/H'
