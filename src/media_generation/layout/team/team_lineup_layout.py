from dataclasses import dataclass

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.layout.layout import Layout
from src.media_generation.models.team import Team
from src.media_generation.readers.race_reader_models.race import Race


@dataclass
class TeamLineupLayout(Layout):
    team: Team = None

    def _render_base_image(self, context: dict = {}) -> PngImageFile:
        if not self.team:
            self.children = {}
            return super()._render_base_image(context)
        self.children['logo'].path = self.team.get_lineup_logo_path()
        race:Race = context.get('race')
        if race:
            pilots = race.get_pilots(self.team)
        else:
            config: GeneratorConfig = context.get('config')
            pilots = config.get_pilots(self.team)
        if 'pilot_1' in self.children:
            self.children['pilot_1'].pilot = pilots[0] if pilots and len(pilots) > 0 else None
        if 'pilot_2' in self.children:
            self.children['pilot_2'].pilot = pilots[1] if pilots and len(pilots) > 1 else None
        return super()._render_base_image(context)

    def _get_children_context(self, context: dict= {}):
        if self.team:
            return dict(context, team=self.team)
        return super()._get_children_context(context)
