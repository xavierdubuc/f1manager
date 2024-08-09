from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.readers.general_ranking_models.pilot_ranking import PilotRankingRow
from src.media_generation.generators.pilots_ranking_generator import PilotsRankingGenerator

from ..helpers.transform import *


class LicensePointsGenerator(PilotsRankingGenerator):
    def __init__(self, championship_config: dict, config: GeneratorConfig, season: int, identifier: str = None, *args, **kwargs):
        super().__init__(championship_config, config, season, identifier, *args, **kwargs)
        self.ranking.sort_by_license_points()

    def _get_visual_type(self) -> str:
        return 'license_points'

    def _get_main_title_str(self):
        return 'POINTS DE PERMIS'

    def _get_metric_field(self):
        return 'license_points'

    def _add_content(self, base_img: PngImageFile):
        amount_by_column = self.rows_config['pilots_by_column']
        lateral_padding = self.rows_config.get('lateral_padding', 40)
        initial_top = self._get_visual_title_height()
        space_between_pilots = self.rows_config.get('space_between_pilots', 10)
        card_height = self.rows_config['card']['height']

        # body background
        bg_color = self.rows_config.get('bg_color', (55, 55, 55))
        lines_color = self.rows_config.get('lines_color')
        img = Image.new(
            'RGB', (base_img.width, base_img.height-initial_top), bg_color)
        if lines_color:
            draw_lines_all(img, lines_color)
        paste(img, base_img, top=initial_top)

        # ranking rows
        rows = [
            row for row in self.ranking.rows if self._pilot_should_be_shown(row)
        ]
        first_card_left = lateral_padding
        current_left = first_card_left
        current_top = initial_top + self.rows_config.get('padding_top', 30)
        width = base_img.width - lateral_padding * 2
        card_width = (width - space_between_pilots *
                      (amount_by_column - 1)) // amount_by_column
        for i, row in enumerate(rows):
            card = self._get_card(row, card_width, card_height)
            paste(card, base_img, left=current_left, top=current_top)
            if i % amount_by_column == (amount_by_column-1):
                current_top += card_height + space_between_pilots
                current_left = first_card_left
            else:
                current_left += card_width + space_between_pilots

    def _pilot_should_be_shown(self, row: PilotRankingRow) -> bool:
        if self.config.ranking.amount_of_races > 0 and row.amount_of_races == 0:
            return False
        return super()._pilot_should_be_shown(row)

    def _get_card(self, row: PilotRankingRow, width: int, height: int) -> PngImageFile:
        pilot = row.pilot
        config = self.rows_config.get('card', {})
        padding_bottom = config.get('padding_bottom', 10)
        padding_name_points = config.get('padding_name_points', 10)
        padding_name_face = config.get('padding_name_face', 10)
        thickness = config.get('thickness', 10)
        bg_color = config.get('bg_color', 10)
        gradient_color = config['colors'][row.license_points % 21]
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # rectangle
        r = rounded_rectangle(width, height, fill=bg_color,
                              outline=gradient_color, thickness=thickness)
        paste(r, img)

        # face
        face_size = int(0.6 * height)
        face = pilot.get_close_up_image(face_size, face_size)
        face_pos = paste(face, img, top=0)

        # points
        points_font, _ = FontFactory.from_config(config.get('points', {}), 50)
        points = text(str(row.license_points), gradient_color, points_font)
        points_pos = paste(points, img, top=height -
                           points.height - padding_bottom)

        # name
        # font is big to improve quality as generated img will be shrinked down then
        name_font, name_color = FontFactory.from_config(
            config.get('name', {}), 200)

        name = pilot.get_name_image(name_font, name_color)
        remaining_space_between = points_pos.top - \
            face_pos.bottom - padding_name_face - padding_name_points
        name = resize(name, width-40, remaining_space_between)
        paste(name, img, top=face_pos.bottom + padding_name_face)

        return img
