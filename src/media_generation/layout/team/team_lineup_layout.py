from dataclasses import dataclass

from PIL.PngImagePlugin import PngImageFile


from src.media_generation.layout.layout import Layout
from src.media_generation.models.team import Team
from src.media_generation.readers.race_reader_models.race import Race


@dataclass
class TeamLineupLayout(Layout):
    team: Team = None

    def _render_base_image(self, context: dict = {}) -> PngImageFile:
        if not self.team:
            return super()._render_base_image(context)
        self.children['logo'].bg_path = self.team.get_lineup_logo_path()
        race:Race = context.get('race')
        if race:
            if pilots := race.get_pilots(self.team):
                if 'pilot_1' in self.children and len(pilots) > 0:
                    self.children['pilot_1'].pilot = pilots[0]
                if 'pilot_2' in self.children and len(pilots) > 1:
                    self.children['pilot_2'].pilot = pilots[1]
        return super()._render_base_image(context)
