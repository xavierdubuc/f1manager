import copy
import logging
from PIL import Image

from src.media_generation.helpers.generator_config import GeneratorConfig
from src.media_generation.readers.general_ranking_models.team_ranking import TeamRanking
from ..generators.abstract_generator import AbstractGenerator

from ..helpers.transform import *
from ..font_factory import FontFactory
from ..models import Team
from ..data import teams_idx as TEAMS

_logger = logging.getLogger(__name__)

class TeamsRankingGenerator(AbstractGenerator):
    def __init__(self, championship_config: dict, config: GeneratorConfig, season: int, identifier: str = None, *args, **kwargs):
        super().__init__(championship_config, config, season, identifier, *args, **kwargs)
        self.ranking: TeamRanking = self.config.ranking

    def _get_visual_type(self) -> str:
        return 'teams_ranking'

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
            self.text(main_config, "CLASSEMENT ÉQUIPES"),
        ]
        main_top = main_config['top']
        for main_text in main_texts:
            main_pos = paste(main_text, img, left=main_config.get('left', 0), top=main_top)
            main_top = main_pos.bottom + main_config.get('line_space', 10)

        # SUB TITLE
        sub_config = title_config.get('sub', {})
        sub_texts = [
            self.text(sub_config, "POINTS APRÈS", FontFactory.regular),
            self.text(sub_config, f"COURSE {self.config.ranking.amount_of_races}", FontFactory.regular),
        ]
        sub_top = sub_config['top']
        for sub_text in sub_texts:
            sub_left = img.width - sub_text.width - sub_config.get('right', 20)
            sub_pos = paste(sub_text, img, left=sub_left, top=sub_top)
            sub_top = sub_pos.bottom + sub_config.get('line_space', 10)

        return img

    def _add_content(self, base_img: PngImageFile):
        champ_teams = self.championship_config['settings'].get('teams', {})
        all_teams = copy.deepcopy(TEAMS)
        all_teams.update({name: Team(**champ_teams[name]) for name in champ_teams})

        rows_config = self.visual_config.get('rows', {})
        left = rows_config.get('left', 30)
        top = rows_config.get('top', 320)
        rows_width = rows_config.get('width', base_img.width)
        rows_height = rows_config.get('height', base_img.height // len(self.config.ranking.rows))
        background = self._render_image_from_file(rows_config.get('background'), rows_width, rows_height)
        # TODO use param for this (color & enable or not)
        gray_filter = Image.new('RGBA', (background.width, background.height), (225, 225, 225, 150))
        previous_pilot_points = None
        previous_ranking = self.ranking.get_previous_ranking()
        print(previous_ranking)
        for i, row in enumerate(self.config.ranking):
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

            # DETERMINE DELTA FIXME
            if not previous_ranking:
                progression = 0
            else:
                previous_pos, previous_ranking_row = previous_ranking.find(row.team)
                progression = (previous_pos - (i+1)) if previous_pos is not None else None

            # GENERATE AND PASTE IMAGE
            team_ranking_img = self._render_team_ranking_image(all_teams, rows_width, rows_height, position, row.team_name, row.total_points, progression, is_champion)
            paste(team_ranking_img, base_img, left=left, top=top)

            # UPDATE LOOP VARIABLES
            top += rows_height
            previous_pilot_points = row.total_points

    def _render_team_ranking_image(self, teams, width: int, height: int, position: int, team_name: str, points: float, progression: int = 0, is_champion: bool = False) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        config = self.visual_config.get('rows', {})

        # POS
        position_config = config.get('position', {})
        position_img = self._render_position_image(position, position_config)
        self.paste_image(position_img, img, position_config)

        # TEAM (LOGO + NAME)
        team_config = config.get('team', {})
        team_img = self._render_team_image(team_config.get('width', 700), team_config.get('height', height), teams.get(team_name))
        self.paste_image(team_img, img, team_config)

        # PROGRESSION
        prog_config = config.get('progression', {})
        prog_img = self._render_progression_image(progression, prog_config)
        self.paste_image(prog_img, img, prog_config)

        # POINTS
        points_config = config.get('points', {})
        points_img = self._render_points_image(points, points_config)
        self.paste_image(points_img, img, points_config)

        return img

    def _render_team_image(self, width:int, height: int, team:Team) -> PngImageFile:
        card = team.build_card_image(width, height)

        cfg = self.visual_config['rows']['name']
        font_color = team.standing_fg
        team_name = self.text(cfg, team.title, default_color=font_color)
        self.paste_image(team_name, card, cfg)

        return card
