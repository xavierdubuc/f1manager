from PIL import Image
from PIL.PngImagePlugin import PngImageFile

from ..generators.abstract_generator import AbstractGenerator

from ..font_factory import FontFactory

small_font = FontFactory.regular(32)
font = FontFactory.regular(38)
big_font = FontFactory.regular(56)
pilot_font = FontFactory.bold(30)


class ResultsGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'results'

    def _add_content(self, final: PngImageFile):
        title_height = self._get_visual_title_height()

        race_title_height = 80
        right_part_width = final.width // 3
        right_part_height = final.height - title_height
        left_part_width = final.width - right_part_width
        left_part_height = final.height - title_height - race_title_height
        # get race title
        race_title = self.config.race.get_title_image(left_part_width, left_part_height, font, big_font)
        final.paste(race_title, (0, title_height+48), race_title)

        # get circuit image
        circuit_left = int(2 * (final.width / 3))
        circuit_top = title_height + 20
        circuit_img = self.config.race.get_information_image(right_part_width, right_part_height, small_font)
        final.paste(circuit_img, (circuit_left, circuit_top), circuit_img)

        # get rankings image
        rankings_top = (title_height + race_title_height) + 80
        rankings_img = self._get_rankings_image(left_part_width, left_part_height)
        final.paste(rankings_img, (0, rankings_top), rankings_img)

    def _get_rankings_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        top = 0
        hop_between_position = 38
        row_height = 60
        padding_left = 20
        padding_between = 40
        padding_right = 40
        col_width = (width - (padding_left+padding_between+padding_right)) // 2
        first_col_left = padding_left
        second_col_left = padding_left + col_width + padding_between
        for index, pilot_name in enumerate(self.config.ranking):
            # Get pilot
            pilot = self.config.race.get_pilot(pilot_name)

            pos = index + 1
            left = first_col_left if index % 2 == 0 else second_col_left
            if pilot:
                has_fastest_lap = pilot_name == self.config.fastest_lap.pilot.name
                ranking_pilot_image = pilot.get_ranking_image(
                    pos, col_width, row_height, small_font, pilot_font, has_fastest_lap)
                img.paste(ranking_pilot_image, (left, top))
                top += hop_between_position
        return img
