from dataclasses import dataclass

from src.media_generation.layout.image_layout import ImageLayout


@dataclass
class FastestLapIconLayout(ImageLayout):
    def _compute(self):
        super()._compute()
        self.path = "assets/fastest_lap.png"
