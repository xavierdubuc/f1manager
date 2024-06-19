from dataclasses import dataclass

from src.media_generation.readers.race_reader_models.race import Race


@dataclass
class RaceResult:
    race_number: str
    points: str

    # "COMPUTED"
    race: Race = None

    def get_points(self) -> int:
        return int(self.points) if self.has_raced() else 0

    def has_raced(self) -> bool:
        return self.points != 'abs'
