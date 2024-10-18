from dataclasses import dataclass
from typing import Any, Dict

from PIL.PngImagePlugin import PngImageFile
from PIL import Image, ImageFilter


from src.media_generation.helpers.transform import resize
from src.media_generation.layout.layout import Layout


@dataclass
class ImageLayout(Layout):
    path: str = None
    keep_ratio: bool = True
    gaussian_blur: int = False
    crop_and_zoom_center: bool = False
    hsv_offset: int = 0
    grayscale: bool = False

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
                if self.crop_and_zoom_center:
                    img = self._crop_and_zoom_to_center(bg)
                else:
                    img = self._resize(bg)
            if self.gaussian_blur:
                img = img.filter(ImageFilter.GaussianBlur(self.gaussian_blur))
            if self._get_hsv_offset(context):
                img = self._apply_hsv_offset(img, context)
            if self._get_grayscale(context):
                img = img.convert('L').convert('RGB')
            return img
        except Exception as e:
            raise Exception(f'A problem occured in layout "{self.name}" : {str(e)}') from e

    def _resize(self, source_img: PngImageFile) -> PngImageFile:
        if self.width and self.height:
            return resize(source_img, height=self.height, width=self.width, keep_ratio=self.keep_ratio)
        elif self.width:
            return resize(source_img, width=self.width, keep_ratio=self.keep_ratio)
        return resize(source_img, height=self.height, keep_ratio=self.keep_ratio)

    def _crop_and_zoom_to_center(self, source_img: PngImageFile) -> PngImageFile:
        if not self.width or not self.height:
            raise Exception("To crop and zoom to center, width and height are mandatory.")
        img = resize(source_img, height=self.height)
        crop_left = (img.width - self.width) // 2
        crop_top = (img.height - self.height) // 2
        return img.crop((crop_left, crop_top, crop_left+self.width, crop_top+self.height))

    def _apply_hsv_offset(self, source_img: PngImageFile, context: Dict[str, Any] = {}) -> PngImageFile:
        hsv = source_img.convert('HSV')
        h, s, v = hsv.split()
        h = h.point(lambda x: self._get_hsv_offset(context))
        return Image.merge('HSV', (h, s, v)).convert('RGB')

    def _get_hsv_offset(self, context: Dict[str, Any] = {}) -> int:
        return self._get_ctx_attr('hsv_offset', context, use_format=True)

    def _get_grayscale(self, context: Dict[str, Any] = {}) -> int:
        return self._get_ctx_attr('grayscale', context, use_format=False)
