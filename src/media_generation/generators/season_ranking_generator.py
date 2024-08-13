import logging
from typing import List
from PIL import Image
from PIL.PngImagePlugin import PngImageFile

from src.media_generation.readers.general_ranking_models.pilot_ranking import PilotRanking, PilotRankingRow
from src.media_generation.readers.general_ranking_models.race_result import RaceResult
from src.media_generation.readers.race_reader_models.race import Race
from src.media_generation.readers.season_ranking_reader import SeasonRankingGeneratorConfig
from ..helpers.transform import *
from ..generators.abstract_generator import AbstractGenerator
from ..models.visual import Visual

_logger = logging.getLogger(__name__)

class SeasonRankingGenerator(AbstractGenerator):
    def __init__(self, championship_config: dict, config: SeasonRankingGeneratorConfig, season: int, identifier: str = None, *args, **kwargs):
        super().__init__(championship_config, config, season, identifier, *args, **kwargs)
        self.races: List[Race] = self.config.races
        self.future_races = set()
        for race in self.races:
            if len(race.race_result.rows) == 0:
                self.future_races.add(race.round)
        self.identifier = self.identifier or 'main'
        self.ranking = self._build_ranking()

    def _get_visual_type(self) -> str:
        return 'season_ranking'

    def _add_content(self, base_img: PngImageFile):
        pilot_name_width = self.visual_config['rows']['pilot'].get('width', 240)
        headers_height = self.visual_config['headers'].get('height', 60)
        global_padding_top = self.visual_config['padding']['top']
        global_padding_left = self.visual_config['padding']['left']
        global_padding_right = self.visual_config['padding']['right']
        rows_padding_left = self.visual_config['headers']['padding'].get('left', 20)
        headers_left = global_padding_left+pilot_name_width+rows_padding_left
        amount_of_races = self.championship_config['seasons'][self.season]['amount_of_races']
        amount_of_suppl_races = 2 # SPRINT + DG
        remaining_width = base_img.width - pilot_name_width - global_padding_left - global_padding_right
        race_width = remaining_width // (amount_of_races + amount_of_suppl_races + 1) # 1 for total header
        rows_top = global_padding_top + headers_height + self.visual_config['rows']['padding'].get('top', 0)

        with Visual.get_fif_logo() as logo:
            logo = resize(logo, headers_height+20, headers_height+20)
            fif_pos = paste(logo, base_img, left=headers_left-rows_padding_left-logo.width, top=global_padding_top//2)

        with Visual.get_fbrt_round_logo() as logo:
            logo = resize(logo, headers_height+20, headers_height+20)
            fbrt_pos = paste(logo, base_img, left=fif_pos.left-logo.width, top=global_padding_top//2)

        title = text(f'RECAP. SAISON {self.season}', (0,0,0), FontFactory.black(40))
        paste(title, base_img, left=(fbrt_pos.left-title.width)//2, top=(rows_top-title.height)//2)

        remaining_height = base_img.height - rows_top
        rows_img = self._get_rows_img(base_img.width - global_padding_left, remaining_height)
        paste(rows_img, base_img, global_padding_left, rows_top)

        self._draw_vertical_bg(base_img, headers_left, race_width)

        headers_img = self._get_headers_img(remaining_width, headers_height, race_width)
        paste(headers_img, base_img, headers_left, global_padding_top)

        rows_points_img = self._get_rows_points_img(base_img.width - global_padding_left, remaining_height, headers_left-rows_padding_left, race_width)
        paste(rows_points_img, base_img, global_padding_left, rows_top)

    def _get_headers_img(self, width:int, height: int, race_width:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))

        total_img = text('TOT', (0,0,0), FontFactory.black(26))
        paste(total_img, img, left=(race_width-total_img.width) // 2)
        left = race_width
        for race in self.races:
            with race.circuit.get_flag() as flag:
                tmpimg = Image.new('RGBA', (race_width, height), (0,0,0,0))
                flag = resize(flag, race_width, height, keep_ratio=True)
                paste(flag, tmpimg)
                paste(tmpimg, img, left=left, top=0)
                left += race_width
        return img

    def _get_rows_img(self, width:int, height:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        amount_of_rows = len(self.ranking.rows)
        row_height = height // amount_of_rows
        padding = 10
        row_content_height = row_height - padding
        top = 0
        for i, ranking_row in enumerate(self.ranking.rows):
            ranking_row_img = self._get_ranking_row_img(i+1, ranking_row, width, row_content_height)
            paste(ranking_row_img, img, left=0, top=top)
            top += row_height
        return img

    def _get_ranking_row_img(self, pos:int, ranking_row:PilotRankingRow, width:int, height:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        position_width = self.visual_config['rows']['position'].get('width', 40)
        pos_txt = self._get_pos_img(position_width, height, pos)
        pos_position = paste(pos_txt, img, left=0)

        pilot_name_width = self.visual_config['rows']['pilot'].get('width', 240)
        pilot = ranking_row.pilot
        card = pilot.team.build_card_image(pilot_name_width - position_width, height)
        card_position = paste(card, img, left=pos_position.right+10)

        # pilot name
        pilot_config = self.visual_config['rows']['pilot']
        pilot_font_name = pilot_config.get('font')
        pilot_font_size = pilot_config['font_size']
        small_font_size_config = pilot_config.get('small_font')
        if small_font_size_config:
            if len(pilot.name) >= small_font_size_config['if']:
                pilot_font_size = small_font_size_config['size']
        pilot_font = FontFactory.get_font(pilot_font_name, pilot_font_size, FontFactory.black)
        pilot_name = text(pilot.name.upper(), pilot.team.standing_fg, pilot_font)
        paste(pilot_name, img, card_position.left + pilot_config['left_padding'])

        # COLOR ROW
        color = pilot.team.transparent_color or pilot.team.standing_bg + (220,)
        bgrow = Image.new('RGBA', (width-card_position.right, height), color)
        paste(bgrow, img, left=card_position.right)

        return img

    def _get_rows_points_img(self, width:int, height:int, first_column_left:int, race_width:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        amount_of_rows = len(self.ranking.rows)
        row_height = height // amount_of_rows
        padding = 10
        row_content_height = row_height - padding
        top = 0
        for i, ranking_row in enumerate(self.ranking.rows):
            ranking_row_img = self._get_ranking_row_points_img(ranking_row, width, row_content_height, first_column_left, race_width)
            paste(ranking_row_img, img, left=0, top=top)
            top += row_height
        return img

    def _get_ranking_row_points_img(self, ranking_row:PilotRankingRow, width:int, height:int, first_column_left:int, race_width:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        # TOTAL + POINTS
        total_bg = Image.new('RGBA', (race_width, height), (0,0,0,0))
        total = text(str(ranking_row.total_points), (0,0,0), FontFactory.black(34))
        left = first_column_left
        paste(total, total_bg, left=(total_bg.width-total.width)//2 + 8)
        paste(total_bg, img, left=left)

        for race in self.races:
            left += race_width
            row = race.race_result.get(ranking_row.pilot)
            bg = Image.new('RGBA', (race_width, height), (0,0,0,0))
            font = FontFactory.bold(30)
            if race.round in self.future_races:
                continue
            if row:
                if row.points == 0:
                    points_txt = row.split
                    points_color = (255,0,0)
                else:
                    points_txt = str(row.points)
                    points_color = (0,0,0)
            else:
                points_txt = 'abs'
                points_color = (200, 200, 200)
            points = text(points_txt, points_color, font)
            points_left = (bg.width-points.width)//2 + 8
            points_pos = paste(points, bg, left=points_left)


            if row:
                if row.is_driver_of_the_day:
                    draw = ImageDraw.Draw(bg)
                    draw.rectangle(
                        (points_pos.left-8, points_pos.top-6,
                        points_pos.right+8, points_pos.bottom+8),
                        outline=(255, 195, 30),
                        width=4
                    )
                if row.has_fastest_lap:
                    with Image.open(f'assets/fastest_lap.png') as fstst_img:
                        fstst_img = resize(fstst_img, height//2.5, height//2.5)
                        paste(fstst_img, bg, left=bg.width-fstst_img.width, top=5)
            paste(bg, img, left=left)
        return img

    def _get_pos_img(self, width:int, height: int, pos:int):
        position_config = self.visual_config['rows']['position']
        img = Image.new('RGB', (width, height), (0,0,0))

        font_name = position_config.get('font')
        font_size = position_config['font_size']
        font = FontFactory.get_font(font_name, font_size, FontFactory.regular)
        pos_txt = text(str(pos), (255,255,255), font)
        paste(pos_txt, img)
        return img

    def _draw_vertical_bg(self, img:PngImageFile, first_column_left:int, race_width:int):
        left = first_column_left + race_width
        padding_bottom = self.visual_config['padding']['bottom']
        height = img.height - padding_bottom
        while left+race_width < img.width:
            grey = Image.new('RGBA', (race_width, height), (100,100,100,50))
            paste(grey, img, left=left, top=0)
            left += 2 * race_width


    def _build_ranking(self):
        ranking = PilotRanking(
            rows=[
                PilotRankingRow(
                    pilot_name=pilot.name,
                    pilot=pilot,
                    titular=not pilot.reservist,
                    team_name=pilot.team.name,
                    total_points=0, # computeme
                    mean_points=0, # not needed
                    license_points=0, # not needed
                    amount_of_races=0, # not needed
                    race_results=[
                        RaceResult(
                            race_number=race.round,
                            points=race.race_result.get(pilot).points if race.race_result.get(pilot) else 'abs'
                        )
                        for race in self.races
                    ]
                ) for _, pilot in self.config.pilots.items() if self.identifier == 'all' or (not pilot.reservist and self.identifier != 'reservists') or (pilot.reservist and self.identifier == 'reservists')
            ]
        )
        kept_rows = []
        for r in ranking.rows:
            if self.identifier != 'reservists' and all(res.points == 'abs' for res in r.race_results):
                continue
            r.total_points = sum(result.points if isinstance(result.points, int) else 0 for result in r.race_results)
            kept_rows.append(r)
        ranking.rows = kept_rows
        ranking.sort_by_points()
        return ranking
