from dataclasses import dataclass

from src.media_generation.layout.image_layout import ImageLayout


@dataclass
class FIFLogoLayout(ImageLayout):
    shape: str = "wide"
    color: str = "white"

    def _compute(self):
        super()._compute()
        self.path = f"assets/logos/fif/{self.shape}_{self.color}.png"
