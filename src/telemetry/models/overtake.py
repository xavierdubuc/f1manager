from dataclasses import dataclass

from src.telemetry.models.participant import Participant


@dataclass
class Overtake:
    overtaker: Participant
    overtaken: Participant
    lap_num: int
