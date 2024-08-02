import logging
from PIL import Image

from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.readers.general_ranking_models.pilot_ranking import PilotRanking, PilotRankingRow
from ..generators.abstract_generator import AbstractGenerator

from ..helpers.transform import *
from ..font_factory import FontFactory
from ..models import Pilot, Team, Visual

_logger = logging.getLogger(__name__)


class PilotsRankingGenerator(AbstractGenerator):
    def __init__(self, championship_config: dict, config: GeneratorConfig, season: int, identifier: str = None, *args, **kwargs):
        super().__init__(championship_config, config, season, identifier, *args, **kwargs)
        key = self.identifier or 'default'
        cfg = self.visual_config['body']
        self.rows_config = cfg.get(key, cfg['default'])
        self.ranking: PilotRanking = self.config.ranking

    def _get_visual_type(self) -> str:
        return 'pilots_ranking'

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        title_config = self.visual_config.get('title', {})
        height = title_config.get('height', 300)
        img = Image.new('RGBA', (base_img.width, height), (0,0,0,0))

        # MAIN LOGO
        main_logo_config = title_config.get('main_logo')
        if main_logo_config:
            self.paste_image_from_config(main_logo_config, img)

        # SECOND LOGO
        secondary_logo_config = title_config.get('secondary_logo')
        if secondary_logo_config:
            self.paste_image_from_config(secondary_logo_config, img)

        # MAIN TITLE
        main_config = title_config.get('main', {})
        main_texts = [
            self.text(main_config, f"SAISON {self.season}", FontFactory.black),
            self.text(main_config, "CLASSEMENT PILOTES"),
        ]
        main_top = main_config['top']
        for main_text in main_texts:
            main_pos = paste(main_text, img, left=main_config.get('left', 0), top=main_top)
            main_top = main_pos.bottom + main_config.get('line_space', 10)

        # SUB TITLE
        if self.config.ranking.amount_of_races > 0:
            sub_config = title_config.get('sub', {})
            sub_text = self.text(sub_config, f"POINTS APRÈS COURSE {self.config.ranking.amount_of_races}", FontFactory.regular)
            sub_top = sub_config['top']
            sub_left = img.width - sub_text.width - sub_config.get('right', 20)
            paste(sub_text, img, left=sub_left, top=sub_top)

        return img

    def _add_content(self, base_img: PngImageFile):
        rows_lefts = self.rows_config['columns']
        amount_by_column = self.rows_config['pilots_by_column']
        body_config = self.visual_config.get('body', {})
        row_index = 0
        column_index = 0
        initial_top = top = body_config.get('top', 320)
        rows_width = self.rows_config.get('width', base_img.width)
        rows_height = self.rows_config.get('height', base_img.height // len(self.config.ranking.rows))
        background = self._render_image_from_file(body_config.get('background'), rows_width, rows_height)
        gray_filter = Image.new('RGBA', (background.width, background.height), (225, 225, 225, 150))

        previous_pilot_points = None
        previous_ranking = self.ranking.get_previous_ranking()
        for i, row in enumerate(self.config.ranking):
            if column_index >= len(rows_lefts):
                continue

            # SHOW ROW OR NOT (ex: if identifier is "main" and pilot is reservist)
            if not self._pilot_should_be_shown(row.pilot):
                continue

            left = rows_lefts[column_index]
            if background:
                paste(background, base_img, left, top)
            if i % 2 == 0:
                paste(gray_filter, base_img, left, top)

            is_champion = False # i == 0 # FIXME
            # DETERMINE POSITION
            points = row.total_points
            if previous_pilot_points is not None and previous_pilot_points == points:
                position = '-'
            else:
                position = str(i+1)

            # DETERMINE DELTA
            if not previous_ranking:
                progression = 0
            else:
                previous_pos, previous_ranking_row = previous_ranking.find(row.pilot)
                progression = (previous_pos - (i+1)) if previous_pos is not None else None

            # GENERATE AND PASTE IMAGE
            pilot_config = body_config.get('pilot', {})
            pilot_ranking_img = self._render_pilot_ranking_image(
                pilot_config.get('width', rows_width),
                pilot_config.get('height', rows_height),
                row.pilot,
                position,
                points,
                progression
            )
            paste(pilot_ranking_img, base_img, left, top)

            # UPDATE LOOP VARIABLES
            previous_pilot_points = points
            if row_index == amount_by_column - 1:
                top = initial_top
                column_index += 1
                row_index = 0
            else:
                top += rows_height
                row_index += 1
        return

    def _pilot_should_be_shown(self, row:PilotRankingRow) -> bool:
        if self.identifier == 'main':
            return not row.pilot.reservist
        if self.identifier == 'reservists':
            return row.pilot.reservist
        return True

    def _render_pilot_ranking_image(self, width: int, height: int, pilot: Pilot, position: str, points: float, delta: str, is_champion: bool = False) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        config = self.visual_config.get('body', {}).get('pilot', {})

        # POS
        position_config = config.get('position', {})
        position_img = self._render_position_image(position, position_config)
        self.paste_image(position_img, img, position_config)

        # TEAM
        team_config = config.get('team', {})
        team_card_img = pilot.team.render_logo(
            team_config.get('width', 190), team_config.get('height', 104), team_config.get('logo_height', 80)
        )
        self.paste_image(team_card_img, img, team_config)

        # FACE
        face_config = config.get('face', {})
        face = pilot.get_face_image(face_config['width'], face_config['height'])
        self.paste_image(face, img, face_config)

        # NAME
        name_config = config.get('name', {})
        name_img = self.text(name_config, pilot.name.upper())
        self.paste_image(name_img, img, name_config)

        # PROGRESSION
        prog_config = config.get('progression', {})
        prog_img = self._render_progression_image(delta, prog_config)
        self.paste_image(prog_img, img, prog_config)

        # POINTS
        points_config = config.get('points', {})
        points_img = self._render_points_image(points, points_config)
        self.paste_image(points_img, img, points_config)

        return img
