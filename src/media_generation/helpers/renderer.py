from dataclasses import dataclass
import importlib

from src.media_generation.run_config import RunConfig
from .generator_config import GeneratorConfig


@dataclass
class Renderer:
    run_config: RunConfig

    def render(self, config: GeneratorConfig, championship_config: dict, season:int, identifier: str = None, *args, **kwargs):
        visuals_config = championship_config['settings']['visuals']
        custom_generator = visuals_config.get(config.type, {}).get('generator')
        if custom_generator:
            generator_module = importlib.import_module(custom_generator['package'])
            generator_cls = getattr(generator_module, custom_generator['name'])
        else:
            generator_cls = self.run_config.Generator
            if isinstance(generator_cls, dict):
                generator_module = importlib.import_module(generator_cls['package'])
                generator_cls = getattr(generator_module, generator_cls['name'])
        generator = generator_cls(championship_config, config, season, identifier, *args, **kwargs)
        return generator.generate()
