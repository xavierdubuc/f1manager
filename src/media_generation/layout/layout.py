import copy
import logging
from PIL.PngImagePlugin import PngImageFile
from PIL import Image
from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Tuple

from src.media_generation.helpers.transform import Dimension

_logger = logging.getLogger(__name__)

DEFAULT_OPACITY = 255
DEFAULT_BG = (0, 0, 0, 0)
TEMPLATE_PREFIX = '__TPL__'

@dataclass
class Layout:
    # Identifier
    name: str

    # Size
    width: int = None
    height: int = None

    # Pasting information
    left: int = None
    right: int = None
    top: int = None
    bottom: int = None

    # Colors
    bg: Tuple[int, int, int, int] = DEFAULT_BG
    fg: Tuple[int, int, int, int] = (0, 0, 0, DEFAULT_OPACITY)

    # Compositing
    children: Dict[str, "Layout"] = field(default_factory=dict)
    templates: Dict[str, "LayoutTemplate"] = field(default_factory=dict)

    @property
    def size(self):
        return (self.width, self.height)

    def __post_init__(self):
        self.bg = self._ensure_rgba(self.bg)
        self.fg = self._ensure_rgba(self.fg)

    def render(self, context: Dict[str, Any] = {}) -> PngImageFile:
        self.width = self.width or context.get('width')
        self.height = self.height or context.get('height')
        img = self._render_base_image(context)
        if img:
            context.update({
                'width': img.width,
                'height': img.height,
            })
            if self.templates:
                self._process_templates(img, context)
            if self.children:
                self._paste_children(img, context)
            return img

    def paste_on(self, on: PngImageFile, context: Dict[str, Any] = {}) -> Dimension:
        try:
            img = self.render(context)
            if not img:
                _logger.debug("No img generated, won't paste")
                return None
            left = self.left
            if left is None and self.right is not None:
                left = on.width - img.width - self.right

            top = self._get_top(context)
            if top is None and self.bottom is not None:
                top = on.height - img.height - self.bottom

            left = left if left is not None else (on.width-img.width) // 2
            top = top if top is not None else (on.height-img.height) // 2

            if img.mode == 'RGB':
                _logger.debug(f"Pasting RGB at ({left}, {top})")
                on.paste(img, (left, top))
            else:
                if on.mode == 'RGBA' == img.mode:
                    _logger.debug(f"Alpha compositing at ({left}, {top})")
                    on.alpha_composite(img, (left, top))
                else:
                    _logger.debug(f"Pasting RGBA at ({left}, {top})")
                    on.paste(img, (left, top), img)

            return Dimension(left, top, left+img.width, top+img.height)
        except Exception as e:
            raise Exception(f'A problem occured when pasting layout "{self.name}" : {str(e)}') from e

    def _get_top(self, context: Dict[str, Any] = {}) -> int:
        return self.top

    def _ensure_rgba(self, value):
        if value is None:
            return DEFAULT_BG
        if isinstance(value, int):
            return (value, value, value, DEFAULT_OPACITY)
        if isinstance(value, tuple) and len(value) == 3:
            return value + (DEFAULT_OPACITY, )
        return value

    def _render_base_image(self, context: Dict[str, Any] = {}) -> PngImageFile:
        if not self.width or not self.height:
            raise Exception(f'Layout "{self.name}" has no size')
        return Image.new('RGBA', self.size, self._get_bg(context))

    def _paste_children(self, img: PngImageFile, context: Dict[str, Any] = {}):
        for key, child in self.children.items():
            if key.startswith(TEMPLATE_PREFIX):
                i, child = child
                child_ctx = self._get_template_instance_context(i, context)
                if not child_ctx:
                    continue
                context.update(child_ctx)
            self._paste_child(img, key, child, context)

    def _process_templates(self, img: PngImageFile, context: Dict[str, Any] = {}):
        for template in self.templates.values():
            _logger.info(f'Processing template {template.layout.name}')
            self.children.update(template.get_layouts())

    def _paste_child(self, img: PngImageFile, key: str, child: "Layout", context: Dict[str, Any] = {}):
        _logger.debug(f'Pasting child {key} on layout {self.__class__.__name__}')
        child.paste_on(img, self._get_children_context(context))

    def _get_bg(self, context: Dict[str, Any] = {}) -> Tuple[int, int, int, int]:
        return self._get_ctx_attr('bg', context, use_format=True)

    def _get_fg(self, context: Dict[str, Any] = {}) -> Tuple[int, int, int, int]:
        return self._get_ctx_attr('fg', context, use_format=True)

    def _get_children_context(self, context: Dict[str, Any] = {}) -> Dict[str, Any]:
        return context

    def _get_template_instance_context(self, i:int, context: Dict[str, Any] = {}):
        return {}

    def _get_ctx_attr(self, attr_name:str, context: Dict[str, Any] = {}, use_format=False) -> Any:
        attr = getattr(self, attr_name)
        if isinstance(attr, str):
            try:
                if use_format:
                    return eval(attr.format(**context))
                return eval(attr, context)
            except KeyError as e:
                print(context.keys())
                raise Exception(f"Missing variable \"{e.args[0]}\" in rendering context")
        return attr

@dataclass
class LayoutTemplate:
    layout: Layout
    instances: List[Dict[str, int]]

    def get_layouts(self) -> Dict[str, Tuple[int, Layout]]:
        out = {}
        for i, instance_values in enumerate(self.instances):
            instance = copy.deepcopy(self.layout)
            instance.name = f'{self.layout.name}_{i}'
            for field, value in instance_values.items():
                setattr(instance, field, value)
            out[f'{TEMPLATE_PREFIX}{instance.name}'] = (i,instance)
        return out
