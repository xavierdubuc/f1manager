import logging
from typing import List, Union
import xml.etree.ElementTree as ET
from src.media_generation.layout import Layout
import src.media_generation.layout as Layouts
from src.media_generation.layout.layout import LayoutTemplate
from src.media_generation.layout.polygons_layout import Polygon
_logger = logging.getLogger(__name__)

TEMPLATE_TAG_NAME = "LayoutTemplate"
STRING_FIELDS = ("name", "font_name", )
SPECIAL_TAGS = ("Polygon", "Edge")
POLYGONS_TAG = "Polygons"

# TODO part in template to specify needed values
# -> replacing RunConfig & la manière dont on lit le fichier excel
class XMLParser:
    def parse(self, filepath) -> Layout:
        tree = ET.parse(filepath)
        root = tree.getroot()
        return self.convert(root)

    def convert(self, node: ET.Element) -> Union[Layout, LayoutTemplate]:
        # Template
        if node.tag == TEMPLATE_TAG_NAME:
            layout_or_template = self._node_to_template(node)
            layout = layout_or_template.layout
            node = node.find('Template/*')
            _logger.debug(f"Template --> new node is {node.tag}")
        # Simple layout
        else:
            layout_or_template = self._node_to_layout(node)
            layout = layout_or_template

        if not layout_or_template:
            return
        # Process children
        for subnode in node:
            sublayout = self.convert(subnode)
            if not sublayout:
                continue
            if isinstance(sublayout, LayoutTemplate):
                layout.templates[sublayout.layout.name] = sublayout
            else:
                layout.children[sublayout.name] = sublayout
        return layout_or_template

    def _node_to_layout(self, node: ET.Element) -> Layout:
        if node.tag in SPECIAL_TAGS:
            return
        layout_class_name = f"{node.tag}Layout" if node.tag != "Layout" else "Layout"
        try:
            LayoutClass = getattr(Layouts, layout_class_name)
            layout = LayoutClass(name=node.tag, children={})
        except AttributeError:
            _logger.info(f"Layout \"{layout_class_name}\" does not exist, using default")
            layout = Layout(name=node.tag, children={})
        for field, str_value in node.attrib.items():
            if not hasattr(layout, field):
                raise ValueError(f"{layout.__class__.__name__} does not support field {field}")
            value = self._get_attr_value(field, str_value)
            setattr(layout, field, value)
        if node.tag == POLYGONS_TAG:
            layout.polygons = self._parse_polygons(node)
        return layout

    def _node_to_template(self, node:ET.Element) -> LayoutTemplate:
        layout_node = node.find('Template/*')
        layout = self._node_to_layout(layout_node)
        instances_nodes = node.find('Instances').findall('Instance')
        instances = []
        for instance_node in instances_nodes:
            instance_values = {
                field: self._get_attr_value(field, str_value)
                for field, str_value in instance_node.attrib.items()
            }
            instances.append(instance_values)
        return LayoutTemplate(layout, instances)

    def _parse_polygons(self, node:ET.Element) -> List[Polygon]:
        polygons = []
        polygons_node = node.findall('Polygon')
        for polygon_node in polygons_node:
            polygons.append(Polygon(
                color=self._get_attr_value("color", polygon_node.attrib.get('color', None)),
                edges = [
                    (int(e.attrib['x']), int(e.attrib['y'])) for e in polygon_node.findall('Edge')
                ]
            ))
        return polygons

    def _get_attr_value(self, field:str, str_value:str):
        if field in STRING_FIELDS:
            return str_value
        try:
            value = eval(str_value)
        except (NameError, SyntaxError):
            value = str_value
        return value
