from dataclasses import dataclass

from src.media_generation.layout.bg_image_layout import BgImageLayout


@dataclass
class FlagLayout(BgImageLayout):
    bg_path: str = None

    def __post_init__(self):
        super().__post_init__()
        self.bg_path = 'assets/circuits/flags/{circuit.id}.png'
