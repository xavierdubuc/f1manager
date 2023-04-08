from dataclasses import dataclass

from PIL import Image, ImageDraw


@dataclass
class Circuit:
    id: str
    name: str
    lap_length: float
    best_lap: str
    city: str = None

    def get_flag(self):
        return Image.open(f'assets/circuits/flags/{self.id}.png')

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
