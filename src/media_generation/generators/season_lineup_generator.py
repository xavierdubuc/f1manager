from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from ..models.pilot import Pilot
from ..helpers.transform import *
from ..generators.abstract_generator import AbstractGenerator

RESERVISTS_MODE = True

class SeasonLineupGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'season_lineup'

    def _add_content(self, base_img: PngImageFile):
        main_pilots_objects = {k:p for i, (k, p) in enumerate(self.config.pilots.items()) if i < 20 }
        reservists_objects = {k:p for i, (k, p) in enumerate(self.config.pilots.items()) if i >= 20 }
        pilots_objects = (main_pilots_objects if not RESERVISTS_MODE else reservists_objects).values()
        if self.visual_config.get('sort'):
            pilots = sorted(pilots_objects, key=lambda x: int(x.number) if x.number.isnumeric() else 999)
        else:
            pilots = list(pilots_objects)

        title_height = 200
        title_img = self._get_title_img(base_img.width, title_height)
        paste(title_img, base_img, top=0)

        row_config = self.visual_config.get('rows', {})
        even_left, odd_left = row_config.get('columns', [20, 540])
        even_top = row_config.get('top')
        odd_top = even_top + row_config.get('vertical_shift', 20)
        row_width = row_config.get('width', 500)
        row_height = row_config.get('height', 84)
        for i,pilot in enumerate(pilots):
            top = even_top if i % 2 == 0 else odd_top
            left = even_left if i % 2 == 0 else odd_left
            pilot_img = self._render_pilot_image(pilot, row_width, row_height)
            paste(pilot_img, base_img, left=left, top=top)
            if i % 2 == 0:
                even_top += row_height
            else:
                odd_top += row_height

    def _get_title_img(self, width:int, height:int) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))

        left_logo_config = self.visual_config.get('left_logo')
        if left_logo_config:
            with Image.open(left_logo_config['path']) as left_logo:
                left_logo = resize(left_logo, height, left_logo_config['height'])
                paste(left_logo, img, left=left_logo_config['left'], top=left_logo_config['top'])

        right_logo_config = self.visual_config.get('right_logo')
        if right_logo_config:
            with Image.open(right_logo_config['path']) as right_logo:
                right_logo = resize(right_logo, height=right_logo_config['height'])
                paste(right_logo, img, left=img.width-right_logo.width, top=height-right_logo.height + right_logo_config['top'])

        font_size = self.visual_config['title'].get('font_size', 60)
        font_color = self.visual_config['title'].get('font_color', (0,0,0))
        font_name = self.visual_config['title'].get('font')
        if font_name:
            font = FontFactory.font(font_name, font_size)
        else:
            font = FontFactory.black(font_size)
        title_text = text(f'SAISON {self.season}', font_color, font)
        title2_text = text('RÉSERVISTES' if RESERVISTS_MODE else 'PILOTES', font_color, font)
        title_top = (height-(title_text.height+title2_text.height)) // 2
        title_pos = paste(title_text, img, top=title_top)
        paste(title2_text, img, top=title_pos.bottom+20)
        return img

    def _render_pilot_image(self, pilot:Pilot, width:int, height:int) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        rows_config = self.visual_config.get('rows', {})
        background_config = rows_config.get('background')
        background = self._render_image_from_file(background_config.get(
            'path'), background_config.get('width', width), background_config.get('height', height))
        self.paste_image(background, img, background_config)

        number_config = rows_config.get('number', {})
        number_container = Image.new('RGBA', (number_config.get('width', width), number_config.get('height', height)))
        number_img = self.text(number_config, str(pilot.number or '-'),
                               security_padding=number_config.get('stroke_width', -1) + 1,
                               stroke_fill=pilot.team.secondary_color, default_color=pilot.team.main_color)
        paste(number_img, number_container)
        self.paste_image(number_container, img, number_config)

        # TEAM
        team_config = rows_config.get('team', {})
        team_card_img = pilot.team.render_logo(
            team_config.get('width', 190), team_config.get(
                'height', height), team_config.get('logo_height', int(.8 * height))
        )
        self.paste_image(team_card_img, img, team_config)

        # FACE
        face_config = rows_config.get('face', {})
        face = pilot.get_face_image(face_config.get('width', 100), face_config.get('height', height))
        self.paste_image(face, img, face_config)

        # NAME
        name_config = rows_config.get('name', {})
        name_img = self.text(name_config, pilot.name.upper())
        self.paste_image(name_img, img, name_config)

        return img
