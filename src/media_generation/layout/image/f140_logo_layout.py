from dataclasses import dataclass

from src.media_generation.layout.image_layout import ImageLayout


@dataclass
class F140LogoLayout(ImageLayout):
    def _compute(self):
        super()._compute()
        self.path = "assets/logos/F140/black.png"
