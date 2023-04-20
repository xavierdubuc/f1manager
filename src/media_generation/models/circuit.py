from dataclasses import dataclass

from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from ..helpers.transform import text, paste

from src.media_generation.font_factory import FontFactory


@dataclass
class Circuit:
    id: str
    name: str
    lap_length: float
    best_lap: str
    city: str = None

    def get_flag(self) -> PngImageFile:
        return self._get_assets('flags')

    def get_photo(self) -> PngImageFile:
        return self._get_assets('photos')

    def get_map(self) -> PngImageFile:
        return self._get_assets('maps')

    def get_full_name_img(self,
                          width:int,
                          height:int,
                          name_font=FontFactory.black(24),
                          city_font=FontFactory.black(20),
                          name_color=(230,0,0),
                          city_color=(255,255,255)
        ) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        name_img = text(self.name.upper(), name_color, name_font)
        city_img = text(self.city.upper(), city_color, city_font)

        padding = 10
        full_height = name_img.height + city_img.height
        top = (height-(full_height+2*padding))//2
        name_position = paste(name_img, img, left=0, top=top, use_obj=True)

        paste(city_img, img, left=0, top=name_position.bottom+padding)
        return img

    def _get_assets(self, asset_type):
        return Image.open(f'assets/circuits/{asset_type}/{self.id}.png')
