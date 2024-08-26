from dataclasses import dataclass

from PIL.PngImagePlugin import PngImageFile
from PIL import Image, ImageFilter


from src.media_generation.helpers.transform import resize
from src.media_generation.layout.layout import Layout
from src.media_generation.readers.race_reader_models.race_ranking import RaceRankingRow


@dataclass
class TyresLayout(Layout):
    tyre_size:int = 20
    tyre_spacing:int = 0

    def _render_base_image(self, context: dict = {}) -> PngImageFile:
        try:
            row : RaceRankingRow= context.get('race_ranking_row')
            if not row or not row.tyres:
                return super()._render_base_image(context)

            tyre_imgs = []
            for tyre in row.tyres:
                with Image.open(f'./assets/tyres/{tyre}.png') as tyre_img:
                    tyre_imgs.append(resize(tyre_img, self.tyre_size, self.tyre_size))

            expected_width = self.tyre_size * len(tyre_imgs) + (len(tyre_imgs) - 1) * self.tyre_spacing
            img = Image.new('RGBA', (expected_width, self.height), self._get_bg(context))
            current_left = 0
            for tyre_img in tyre_imgs:
                img.paste(tyre_img, (current_left, 0), tyre_img)
                current_left += (self.tyre_size + self.tyre_spacing)

            if self.width and self.height and self.width < expected_width:
                img = resize(img, height=self.height, width=self.width)
            img.save('test.png')
            return img
        except Exception as e:
            raise Exception(f'A problem occured in layout "{self.name}" : {str(e)}') from e
