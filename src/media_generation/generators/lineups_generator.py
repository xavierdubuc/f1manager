from PIL import Image
from PIL.PngImagePlugin import PngImageFile

from src.media_generation.models.pilot import Pilot
from src.media_generation.models.team import Team
from src.media_generation.models.visual import Visual
from ..generators.abstract_race_generator import AbstractRaceGenerator
from ..helpers.transform import *


class LineupGenerator(AbstractRaceGenerator):
    def _get_visual_type(self) -> str:
        return 'lineups'

    def _render_initial_image(self) -> PngImageFile:
        initial_img = super()._render_initial_image()
        prll_color = self.visual_config['alt_background']
        draw = ImageDraw.Draw(initial_img)
        parallelograms = [
            (
                (0, 263),
                (0, 510),
                (445, 64),
                (200, 64),
            ),
            (
                (424, 523),
                (1158, 523),
                (605, 1080),
                (0, 1080),
                (0, 950),
            ),
            (
                (738, 523),
                (1468, 523),
                (1920, 74),
                (1920, 0),
                (1256, 0),
            ),
            (
                (1352, 1080),
                (1920, 1080),
                (1920, 523),
                (1908, 523)
            )
        ]
        for parallelogram in parallelograms:
            draw.polygon(parallelogram, prll_color)
        return initial_img

    def _add_content(self, base_img: PngImageFile):
        self._render_logos(base_img)
        self._render_teams(base_img)
        self._render_race(base_img)
        self._render_date(base_img)
        self._render_circuit(base_img)

    def _render_logos(self, base_img: PngImageFile):
        logo_configs = self.visual_config.get('logos', [])
        if not logo_configs:
            return
        for logo_config in logo_configs:
            self.paste_image_from_config(logo_config, base_img)

    def _render_teams(self, base_img: PngImageFile):
        teams_positions = self.visual_config.get('teams', [])
        for team_position_config, team in zip(teams_positions, self.config.teams):
            self._render_team(base_img, team, team_position_config)

    def _render_race(self, base_img:PngImageFile):
        config = self.visual_config.get('race', {})

        # TYPE
        type_config = config.get('type', {})
        type_w = type_config.get('width', 100)
        type_h = type_config.get('height', type_w)
        type_img = self.race_renderer.get_type_image(
            type_w, type_h, text_font=FontFactory.regular(20)
        )
        self.paste_image(type_img, base_img, type_config)

        # TEXT "LINE-UP"
        text_config = config.get('text', {})
        content = text_config.get('content', 'LINE-UP').upper()
        text_img = self.text(text_config, content, default_font=FontFactory.black)
        self.paste_image(text_img, base_img, text_config)

    def _render_date(self, base_img:PngImageFile):
        config = self.visual_config.get('date', {})
        w = config.get('width')
        h = config.get('height')
        content = f"{self.race.full_date.day} {month_fr(self.race.full_date.month)}"
        date_img = text_hi_res(content, config.get('font_color', (255, 255, 255)),
                    FontFactory.regular(40), w, h, use_background=(0, 0, 0))
        self.paste_image(date_img, base_img, config)

        hour_config = self.visual_config.get('hour', {})
        hour_w = config.get('width')
        hour_h = config.get('height')
        date_img = text_hi_res(self.race.hour, hour_config.get('font_color', (255, 255, 255)),
                    FontFactory.regular(40), hour_w, hour_h, use_background=(0, 0, 0))
        self.paste_image(date_img, base_img, hour_config)

    def _render_circuit(self, base_img:PngImageFile):
        config = self.visual_config.get('circuit', {})
        flag_config = config.get('flag', {})
        flag_w = flag_config.get('width', 100)
        flag_h = flag_config.get('height', 100)
        with self.race.circuit.get_flag() as flag_img:
            flag_img = resize(flag_img, flag_w, flag_h)
        self.paste_image(flag_img, base_img, flag_config)

        name_config = config.get('name', {})
        name_content = f'{self.race.circuit.city}'.upper()
        name_img = text_hi_res(
            name_content, name_config.get('color', (255,255,255)),
            FontFactory.regular(40),
            name_config.get('width', 500), name_config.get('height', 40),
        )
        self.paste_image(name_img, base_img, name_config)

    def _render_team(self, base_img:PngImageFile, team:Team, team_position_config: dict):
        config = self.visual_config.get('team', {})
        w = config.get('width', 680)
        h = config.get('height', 200)
        img = Image.new('RGBA', (w,h), (0,0,0,0))

        # LOGO
        logo_config = config.get('logo', {})
        with team.get_lineup_logo() as logo_img:
            logo_img = resize(logo_img, logo_config.get('width'), logo_config.get('height'))
            if logo_img.mode != 'RGBA':
                logo_img = logo_img.convert('RGBA')
            self.paste_image(logo_img, img, logo_config)

        # PILOTS
        pilots = self.race.get_pilots(team)
        pilot_configs = config.get('pilots', {})
        for i, pilot in enumerate(pilots):
            self._render_pilot(pilot, pilot_configs[i%len(pilot_configs)], img)
        
        self.paste_image(img, base_img, team_position_config)

    def _render_pilot(self, pilot:Pilot, config:dict, team_img:PngImageFile):
        w = config.get('width', 338)
        h = config.get('height', 200)
        img = Image.new('RGBA', (w,h), (0,0,0,0))

        # PARALLELOGRAM BOX 
        box_config = config.get('box', {})
        box = pilot.team.get_parallelogram(
            box_config.get('width', w),
            box_config.get('height', 62)
        )

        # HEAD
        face_config = config.get('face', {})
        face_img = pilot.get_close_up_image(height=face_config['height'])
        self.paste_image(face_img, img, face_config)

        # PILOT NAME
        name_config = config.get('name', {})
        name_width = name_config.get('width', w)
        name_height = name_config.get('height', h)
        name = pilot.name.upper()
        name_img = text_hi_res(name, (pilot.team.lineup_fg_color), FontFactory.black(50), name_width, name_height, use_background=pilot.team.lineup_bg_color)
        self.paste_image(name_img, box, name_config)
        self.paste_image(box, img, box_config)

        # Paste image on team image
        self.paste_image(img, team_img, config)
