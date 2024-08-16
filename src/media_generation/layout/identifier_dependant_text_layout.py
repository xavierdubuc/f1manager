from dataclasses import dataclass


from src.media_generation.layout.text_layout import TextLayout


@dataclass
class IdentifierDependantTextLayout(TextLayout):
    def _get_text(self, context: dict = {}) -> str:
        content = self.content['default']
        if 'identifier' in context:
            if context['identifier'] in self.content:
                content = self.content[context['identifier']]
        try:
            if not content:
                return content
            return content.format(**context)
        except KeyError as e:
            raise Exception(f"Missing variable \"{e.args[0]}\" in rendering context")
