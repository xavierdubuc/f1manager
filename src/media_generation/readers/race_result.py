from dataclasses import dataclass


from src.media_generation.models.race import Race

@dataclass
class RaceResult:
    race_number: str
    points: float

    # "COMPUTED"
    race: Race = None
