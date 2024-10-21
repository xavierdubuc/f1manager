from dataclasses import dataclass

from src.media_generation.layout.image_layout import ImageLayout


@dataclass
class BMTLogoLayout(ImageLayout):
    shape: str = "wide"

    def _compute(self):
        super()._compute()
        self.path = f"assets/logos/BMT/{self.shape}.png"
