from dataclasses import dataclass


from src.media_generation.layout.image_layout import ImageLayout


@dataclass
class F1LogoLayout(ImageLayout):
    year: str = "24"
    color: str = "white"

    def _compute(self):
        super()._compute()
        self.path = f"assets/logos/f1/{self.year}_{self.color}.png"
