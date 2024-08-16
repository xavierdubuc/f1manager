from dataclasses import dataclass

from PIL.PngImagePlugin import PngImageFile
from PIL import Image


from src.media_generation.helpers.transform import resize
from src.media_generation.layout.layout import Layout


@dataclass
class ImageLayout(Layout):
    path: str = None

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
                return resize(bg, height=self.height, width=self.width)
        except Exception as e:
            raise Exception(f'A problem occured in layout "{self.name}" : {str(e)}') from e
