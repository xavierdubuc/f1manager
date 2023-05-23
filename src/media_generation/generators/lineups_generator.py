from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from ..generators.abstract_generator import AbstractGenerator
from ..helpers.transform import *


class LineupGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'lineups'

    def _generate_basic_image(self) -> PngImageFile:
        return Image.new('RGB', (1920, 1080), (255,255,255))

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        return None

    def _add_content(self, base_img: PngImageFile):
        draw_lines_all(base_img, (200,200,200), space_between_lines=7)
        amount_of_teams_by_column = 5
        teams_width = int(.38 * base_img.width) #should be near 730
        teams_height = int(.195 * base_img.height)  # should be near 210
        print(f'{teams_width}x{teams_height}')
        teams_left = 5
        teams_top = teams_initial_top = 2
        teams_margin = 5

        center_width = base_img.width - teams_width * 2

        for i, team in enumerate(self.config.race.teams):
            lineup_img = team.get_lineup_image(teams_width, teams_height, self.config.race.get_pilots(team))
            teams_pos = paste(lineup_img, base_img, left=teams_left, top=teams_top, use_obj=True)
            if i == amount_of_teams_by_column - 1:
                teams_top = teams_initial_top
                teams_left += teams_width + center_width - 10
            else:
                teams_top = teams_pos.bottom + teams_margin