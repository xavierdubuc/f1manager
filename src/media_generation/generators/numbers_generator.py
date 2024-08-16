
from dataclasses import dataclass
from ..generators.abstract_generator import AbstractGenerator


@dataclass
class NumbersGenerator(AbstractGenerator):
    visual_type: str = 'numbers'
