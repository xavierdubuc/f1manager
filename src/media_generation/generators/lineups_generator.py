from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from ..generators.abstract_generator import AbstractGenerator


class LineupGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'lineups'

    def _add_content(self, base_img: PngImageFile):
        lineup_top = self._get_visual_title_height() + 30
        padding_h = 20
        team_lineups_image = self._get_team_lineups_image(base_img.width - (2 * padding_h), base_img.height - lineup_top)
        base_img.paste(team_lineups_image, (padding_h, lineup_top), team_lineups_image)

    def _get_team_lineups_image(self, width:int, height:int):
        padding_bottom = 20
        lineup_height = height - padding_bottom

        img = Image.new('RGBA', (width, lineup_height), (0, 0, 0, 0))
        line_height = int((lineup_height / 10))
        top = 0
        for team in self.config.race.teams:
            lineup_img = team.get_lineup_image(width, line_height, self.config.race.get_pilots(team))
            img.paste(lineup_img, (0, top))
            top += line_height
        return img