import logging
from dataclasses import dataclass, field
from PIL import Image, ImageDraw
from src.media_generation.readers.race_reader_models.race_ranking import RaceRankingRow

from ..font_factory import FontFactory
from ..helpers.transform import *


_logger = logging.getLogger(__name__)

@dataclass
class RankingRowRenderer:
    ranking_row: RaceRankingRow
    visual_config: dict = field(default_factory=dict)

    def __post_init__(self):
        self.has_NT_or_DSQ = self.ranking_row.split in ('NT', 'DSQ')
        fg_and_bg_config = self._get_fg_and_bg_config()
        self.fg_color = fg_and_bg_config['foreground']
        self.bg_color = fg_and_bg_config['background']
        if self.ranking_row.position == 1 or self.has_NT_or_DSQ or not self.ranking_row.split:
            self.split_str = self.ranking_row.split
        else:
            self.split_str = f'+{self.ranking_row.split}'

    def render(self, width:int, height:int) -> PngImageFile:
        # [POS] [PILOT] [TEAM] [TIME/SPLIT] [PTS]
        #       [TYRES]
        # BACKGROUND
        img = self._render_background(width, height)

        # POSITION
        position_config = self.visual_config['position']
        pos_img = self._render_position(position_config['width'], height)
        position_pos = paste(pos_img, img, left=0)

        # PILOT
        pilot_config = self.visual_config['pilot']
        pilot_img = self._render_pilot(pilot_config['width'], height)
        pilot_pos = paste(pilot_img, img, left=position_pos.right)

        # TEAM
        team_config = self.visual_config['team']
        team_img = self._render_team(team_config['width'], height)
        team_pos = paste(team_img, img, left=pilot_pos.right)

        # SPLIT
        split_config = self.visual_config['split']
        split_img = self._render_split(split_config['width'], height//2)
        split_pos = paste(split_img, img, left=team_pos.right, top=0)

        # TYRES
        tyres_config = self.visual_config['tyres']
        tyres_img = self._render_tyres(tyres_config['width'], int(.6 * height))
        paste(tyres_img, img, left=team_pos.right, top=split_pos.bottom)

        # POINTS
        points_config = self.visual_config['points']
        points_img = self._render_points(points_config['width'], height)
        paste(points_img, img, left=width-points_img.width)
        return img

    def _render_background(self, width:int, height:int):
        with Image.open('assets/backgrounds/FBRT/results_row_bg.png') as orig:
            img = resize(orig, width, height, keep_ratio=False)
        bg = Image.new('RGBA', (width, height), self.bg_color)
        paste(bg, img)
        if self.ranking_row.is_driver_of_the_day and self.ranking_row.has_fastest_lap:
            draw = ImageDraw.Draw(img)
            draw.polygon((
                (width//2, height),
                (width//2+50, 0),
                (width, 0),
                (width, height)
            ), fill=self.visual_config['fastest_lap']['background'], width=3)
        return img

    def _render_position(self, width:int, height: int):
        position_config = self.visual_config['position']
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        position_font = FontFactory.get_font(
            position_config.get('font'),
            position_config['font_size'],
            FontFactory.bold
        )
        pos_img = self._get_position_image_sized(
            width // 2,
            int(0.4 * height),
            font=position_font,
            color=position_config['font_color']
        )
        paste(pos_img, img)
        return img

    def _render_pilot(self, width:int, height:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        pilot = self.ranking_row.pilot
        pilot_config = self.visual_config['pilot']
        font = FontFactory.get_font(
            pilot_config.get('font'),
            pilot_config['font_size'],
            FontFactory.bold
        )
        pilot_img = text(pilot.name.upper(), self.fg_color, font)
        paste(pilot_img, img, left=pilot_config['left'], top=pilot_config['top'])
        return img

    def _render_team(self, width:int, height:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        team = self.ranking_row.pilot.team
        team_config = self.visual_config['team']
        logo_width = team_config['logo_width']
        font = FontFactory.get_font(
            team_config.get('font'),
            team_config['font_size'],
            FontFactory.regular
        )
        with team.get_results_logo() as orig:
            logo = resize(orig, logo_width, int(.65*height))
        logo_pos = paste(logo, img, left=0)
        text_img = text(team.display_name, self.fg_color, font)
        paste(text_img, img, left=logo_pos.right + team_config['text_left'], top=team_config.get('text_top', False))
        return img

    def _render_split(self, width:int, height: int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        split_config = self.visual_config['split']
        if not self.ranking_row.split:
            _logger.warning(f'Missing split for "{self.ranking_row.position}. {self.ranking_row.pilot.name}"')
        if self.has_NT_or_DSQ:
            split_fg = self.visual_config['nt'].get('split_foreground', self.fg_color)
            split_font = FontFactory.get_font(split_config.get('font'), split_config['font_size'], FontFactory.bold)
        else:
            split_fg = self.fg_color
            split_font = FontFactory.get_font(split_config.get('font'), split_config['font_size'], FontFactory.regular)
        split_img = text(self.split_str, split_fg, split_font)
        left= (width - split_img.width) - split_config['right']
        paste(split_img, img, left=left, top=split_config['top'])
        return img

    def _render_tyres(self, width:int, height: int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        tyres_config = self.visual_config['tyres']

        if not self.ranking_row.tyres:
            _logger.warning(f'Missing tyres for "{self.ranking_row.position}. {self.ranking_row.pilot.name}"')
        padding = tyres_config['padding']
        size = int(.5 * height)
        current_left = width-size-tyres_config['right']
        for tyre in reversed(self.ranking_row.tyres):
            with Image.open(f'./assets/tyres/{tyre}.png') as tyre_img:
                tyre_img = resize(tyre_img, size, size)
            paste(tyre_img, img, left=current_left, top=tyres_config['top'])
            current_left -= (tyre_img.width + padding)

        return img

    def _render_points(self, width:int, height: int):
        points_config = self.visual_config['points']
        img = Image.new('RGBA', (width, height), points_config['bg_color'])
        points_font = FontFactory.get_font(
            points_config.get('font'),
            points_config['font_size'],
            FontFactory.bold
        )
        points_img = text(f'+{self.ranking_row.points}', points_config['font_color'], points_font)
        paste(points_img, img)
        return img

    def get_details_image(self, width: int, height: int, largest_split_width: int, maximum_tyre_amount:int):
        # [POS] [PILOT] [TYRES] [TIME/SPLIT]
        pilot_config = self.visual_config['pilot']
        split_config = self.visual_config['split']
        position_config = self.visual_config['position']

        pilot_font = FontFactory.get_font(pilot_config.get('font'), pilot_config['font_size'], FontFactory.regular)
        split_font = FontFactory.get_font(split_config.get('font'), split_config['font_size'], FontFactory.regular)

        img = Image.new('RGBA', (width, height), self.bg_color)
        if self.ranking_row.is_driver_of_the_day and self.ranking_row.has_fastest_lap:
            draw = ImageDraw.Draw(img)
            draw.polygon((
                (width//2, height),
                (width//2+50, 0),
                (width, 0),
                (width, height)
            ), fill=self.visual_config['fastest_lap']['background'], width=3)

        # POSITION
        left_padding = 10
        position_font = FontFactory.get_font(
            position_config.get('font'),
            position_config['font_size'],
            FontFactory.regular
        )
        pos_img = self._get_position_image(font=position_font, color=position_config['font_color'])
        left = left_padding + (height-pos_img.width) // 2
        paste(pos_img, img, left=left, top=position_config['top'])
        pos_right = left_padding + height

        # PILOT
        if self.ranking_row.has_fastest_lap:
            show_box = self.visual_config['fastest_lap']['show_box']
        elif self.ranking_row.is_driver_of_the_day:
            show_box = self.visual_config['driver_of_the_day']['show_box']
        else:
            show_box = True
        pilot_width = width - pos_right
        name_top = self.visual_config['pilot']['top']
        pilot_image = self.ranking_row.pilot.get_ranking_image(
            pilot_width, height, pilot_font, show_box, self.fg_color, name_top=name_top
        )
        paste(pilot_image, img, left=pos_right+10)

        # SPLIT
        if not self.ranking_row.split:
            _logger.warning(f'Missing split for "{self.ranking_row.position}. {self.ranking_row.pilot.name}"')
        split_fg = self.fg_color if not self.has_NT_or_DSQ else self.visual_config['nt'].get('split_foreground', self.fg_color)
        split_img = text(self.split_str, split_fg, split_font)
        paste(split_img, img, left=width-split_img.width-20)

        # TYRES
        size_by_tyre = int(self.visual_config['tyres'].get('size_ratio',.75) * height)
        # we take +1 as a security to avoid any overflow on images
        padding = self._get_tyres_padding(maximum_tyre_amount)+self.visual_config['tyres']['security_on_max_padding']
        max_tyres_size = (maximum_tyre_amount * size_by_tyre) + (maximum_tyre_amount * padding)
        tyres_image = self._get_tyres_image(max_tyres_size, height, size_by_tyre)
        paste(tyres_image, img, left=width - largest_split_width - max_tyres_size)

        return img

    def _get_tyres_image(self, width:int, height:int, size_by_tyre:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        current_left = 0
        padding = self._get_tyres_padding(len(self.ranking_row.tyres))
        if not self.ranking_row.tyres:
            _logger.warning(f'Missing tyres for "{self.ranking_row.position}. {self.ranking_row.pilot.name}"')
        for tyre in self.ranking_row.tyres:
            with Image.open(f'./assets/tyres/{tyre}.png') as tyre_img:
                tyre_img = resize(tyre_img, size_by_tyre, size_by_tyre)
            paste(tyre_img, img, left=current_left)
            current_left += (tyre_img.width + padding)
        return img

    def _get_tyres_padding(self, amount_of_tyres:int):
        key = 'padding_more_than_5'
        if amount_of_tyres == 5:
            key = 'padding_5'
        elif amount_of_tyres <= 4:
            key = 'padding_4_or_less'
        return self.visual_config['tyres'][key]

    def _get_position_image(self,
                            font:ImageFont.FreeTypeFont=FontFactory.regular(30),
                            color=(255,255,255)) -> PngImageFile:
        return text(str(self.ranking_row.position), color, font)

    def _get_position_image_sized(self,
                                  width: int,
                                  height: int,
                                  font: ImageFont.FreeTypeFont = FontFactory.regular(30),
                                  color=(255, 255, 255)) -> PngImageFile:
        return text_hi_res(str(self.ranking_row.position), color, font, width, height)

    def _get_fg_and_bg_config(self):
        if self.ranking_row.is_driver_of_the_day:
            key = 'driver_of_the_day'
        elif self.ranking_row.has_fastest_lap:
            key = 'fastest_lap'
        elif self.has_NT_or_DSQ:
            key = 'nt'
        elif self.ranking_row.position % 2 == 0:
            key = 'even'
        else:
            key = 'odd'
        return self.visual_config[key]
