from dataclasses import dataclass

from PIL.PngImagePlugin import PngImageFile
from PIL import Image, ImageFilter


from src.media_generation.helpers.transform import resize
from src.media_generation.layout.layout import Layout


@dataclass
class ImageLayout(Layout):
    path: str = None
    keep_ratio: bool = True
    gaussian_blur: int = False

    def _get_path(self, context: dict = {}) -> str:
        if not self.path:
            return
        try:
            return self.path.format(**context)
        except KeyError as e:
            raise Exception(f"Missing variable \"{e.args[0]}\" in rendering context")

    def _render_base_image(self, context: dict = {}) -> PngImageFile:
        try:
            path = self._get_path(context)
            if not path:
                return super()._render_base_image(context)
            with Image.open(path) as bg:
                if self.width and self.height:
                    img = resize(bg, height=self.height, width=self.width, keep_ratio=self.keep_ratio)
                elif self.width:
                    img = resize(bg, width=self.width, keep_ratio=self.keep_ratio)
                else:
                    img = resize(bg, height=self.height, keep_ratio=self.keep_ratio)
            if self.gaussian_blur:
                return img.filter(ImageFilter.GaussianBlur(self.gaussian_blur))
            return img
        except Exception as e:
            raise Exception(f'A problem occured in layout "{self.name}" : {str(e)}') from e
