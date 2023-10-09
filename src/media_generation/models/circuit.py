from dataclasses import dataclass

from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngImageFile

from src.media_generation.models.best_lap import BestLap
from ..helpers.transform import text, paste

from src.media_generation.font_factory import FontFactory


@dataclass
class Circuit:
    id: str
    name: str
    lap_length: float
    best_lap: str
    city: str = None
    fbrt_best_lap: BestLap = None

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
                          city_color=(255,255,255),
                          padding=10
        ) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        name_img = text(self.name.upper(), name_color, name_font)
        city_img = text(self.city.upper(), city_color, city_font)

        full_height = name_img.height + city_img.height
        top = (height-(full_height+2*padding))//2
        name_position = paste(name_img, img, left=0, top=top)

        paste(city_img, img, left=0, top=name_position.bottom+padding)
        return img

    def get_name_img(self, font=FontFactory.black(24), color=(230, 0, 0)):
        return text(self.name.upper(), color, font)

    def get_city_img(self, font=FontFactory.black(20), color=(255,255,255)):
        return text(self.city.upper(), color, font)

    def get_title_image(self, height: int, font):
        tmp = Image.new('RGBA', (5000, height), (255, 0, 0, 0))
        tmp_draw = ImageDraw.Draw(tmp)
        # circuit name
        _, _, text_width, text_height = tmp_draw.textbbox((0, 0), self.name, font)
        text_top = (height - text_height) // 2
        # flag
        with Image.open(f'assets/circuits/flags/{self.id}.png') as flag:
            flag.thumbnail((height, height), Image.Resampling.LANCZOS)

            padding_between = 30
            width = text_width + flag.width + padding_between
            img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            flag_left = text_width + padding_between
            draw.text((0, text_top), self.name, (255, 255, 255), font)
            img.paste(flag, (flag_left, text_top), flag)
        return img

    def _get_assets(self, asset_type):
        return Image.open(self.get_assets_url(asset_type))

    def get_assets_url(self, asset_type):
        return f'assets/circuits/{asset_type}/{self.id}.png'
