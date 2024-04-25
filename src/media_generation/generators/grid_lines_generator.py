import logging
import os
from PIL import Image
from src.media_generation.generators.grid_generator import GridGenerator

from src.media_generation.readers.race_reader_models.race_ranking import RaceRankingRow

from ..helpers.transform import *
from ..font_factory import FontFactory

_logger = logging.getLogger(__name__)


class GridLinesGenerator(GridGenerator):
    def _get_visual_type(self) -> str:
        return 'grid_lines'

    def _generate_basic_image(self) -> PngImageFile:
        width = self.visual_config['width']
        height = self.visual_config['height']
        _logger.info(f'Output size is {width}px x {height}px')
        img = Image.new('RGBA', (width, height), (30,30,30,0))
        bg = self._get_background_image()
        if bg:
            with bg:
                bg = bg.resize((width, height))
                paste(bg.convert('RGBA'), img)
        return img

    def generate(self):
        path = os.path.dirname(self.config.output)
        left_pilot = right_pilot = None
        row = 1
        for result in self.race.qualification_result.rows:
            if not left_pilot:
                left_pilot = result
                continue
            right_pilot = result
            img = self._generate_row_image(row, left_pilot, right_pilot)
            filename = os.path.join(path, f'row_{row}.png')
            img.save(filename, quality=100)
            _logger.info(f'Image successfully rendered in file "{filename}"')
            left_pilot = None
            row += 1
        return self.config.output

    def _generate_row_image(self, row:int, left:RaceRankingRow, right:RaceRankingRow):
        img = self._generate_basic_image().convert('RGBA')

        middle_width = self.visual_config['middle_grid']['width']
        side_width = (img.width - middle_width) // 2
        middle_img = self._generate_middle_image(row, middle_width, img.height)
        left_pilot_img = self._generate_row_pilot_image(left, side_width, img.height)
        right_pilot_img = self._generate_row_pilot_image(right, side_width, img.height)

        left_pos = paste(left_pilot_img, img, left=0)
        layer = Image.new('RGBA', (img.width, img.height))
        middle_pos = paste(middle_img, layer, left=left_pos.right)
        img.alpha_composite(layer)

        paste(right_pilot_img, img, left=middle_pos.right)

        return img

    def _generate_row_pilot_image(self, row:RaceRankingRow, width:int, height:int):
        is_left = row.position % 2 == 1
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        image_config = self.visual_config['pilot']['image']

        # position
        position_config = self.visual_config['pilot']['position']
        position_img = self._generate_position_image(row.position)
        if is_left:
            pos_left = position_config['left']
        else:
            pos_left = img.width - position_img.width - position_config['left']
        paste(position_img, img, left=pos_left, top=position_config['top'])

        # image
        pilot_img = row.pilot.get_long_range_image()
        side = image_config['side']
        top = image_config['top']
        left = side if is_left else img.width - pilot_img.width - side
        paste(pilot_img, img, left=left, top=top)

        # text on image
        text_img = self._generate_text_image(row, width, height//4)
        bg = Image.new('RGB', (width, text_img.height), (0,0,0, 200))
        top = height-text_img.height
        img.paste(bg, (0, top))
        # paste(bg, img, left=0, top=top)
        paste(text_img, img, left=0, top=top)
        return img

    def _generate_position_image(self, position:int):
        position_color = (255,255,255)
        suffix = {1: 'ER'}.get(position, "ÈME")
        position_img = text(str(position), position_color, FontFactory.black(80))
        suffix_img = text(suffix, position_color, FontFactory.black(30))

        padding = 5
        img = Image.new('RGBA', (position_img.width+suffix_img.width+padding, max(position_img.height, suffix_img.height)), (0,0,0,0))
        position_pos = paste(position_img, img, left=0, top=0)
        paste(suffix_img, img, position_pos.right+padding, top=8)
        return img

    def _generate_text_image(self, row:RaceRankingRow, width:int, height:int):
        is_left = row.position % 2 == 1
        # BG
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        logo_padding = 10

        # TEAM LOGO
        with Image.open(row.pilot.team.get_image()) as logo:
            rlogo = resize(logo, width=int(.25 * width))
            logo_left = logo_padding if is_left else width - rlogo.width - logo_padding
            logo_pos = paste(rlogo, img, logo_left)

        # VERTICAL WHITE LINE
        white_line_padding = 10
        white_line_img = Image.new('RGB', (2, height-20), (255, 255, 255))
        white_line_pos = paste(white_line_img, img, left=(logo_pos.right + white_line_padding) if is_left else logo_pos.left - white_line_padding)

        info_padding = 20
        remaining_width = width - logo.width - logo_padding - white_line_padding - (info_padding) * 2
        # PILOT N°
        number_color = row.pilot.team.alternate_main_color
        number_img = text_hi_res(f'#{row.pilot.number}', number_color, FontFactory.regular(32), remaining_width, int(.2 * height))
        number_pos = paste(number_img, img, top=20, left=(white_line_pos.right + info_padding) if is_left else white_line_pos.left - info_padding - number_img.width)

        # PILOT TIME
        time_img = text_hi_res(row.best_lap, (255,255,255), FontFactory.regular(32), width=int(.5 * remaining_width), height=int(.2 * height))
        if row.position != 1 and row.split != '--:--.---':
            delta_img = text_hi_res(f'+{row.split}', (200,0,0), FontFactory.regular(32), width=int(.4 * remaining_width), height=int(.2 * height))
        else:
            delta_img = None

        time_bottom_padding = 15
        if is_left:
            time_left= (white_line_pos.right + info_padding)
        else:
            time_left = white_line_pos.left - info_padding - time_img.width - (delta_img.width if delta_img else 0)
        time_pos = paste(time_img, img, left=time_left, top=height-time_img.height-time_bottom_padding)
        if delta_img:
            paste(delta_img, img, left=time_pos.right + 10, top=height-delta_img.height-time_bottom_padding)

        # PILOT NAME
        remaining_height = time_pos.top - number_pos.bottom
        name_img = Image.new('RGBA', (remaining_width, remaining_height), (0,0,0,0))
        txt_name_img = text_hi_res(row.pilot.name.upper(), (255,255,255), FontFactory.bold(32), remaining_width, remaining_height)
        if txt_name_img.height > 35:
            txt_name_img = resize(txt_name_img, height=35)
        paste(txt_name_img, name_img, left=0)
        paste(name_img, img, top=number_pos.bottom, left=(white_line_pos.right + info_padding) if is_left else white_line_pos.left - info_padding - name_img.width)

        return img

    def _generate_middle_image(self, row:int, width:int, height:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        first_to_last = False
        # 1 -> 0, 1
        # 2 -> 2, 3
        # 3 -> 4, 5
        current_left_index = 2 * (row-1 )
        current_right_index = current_left_index+1
        current_left = self.race.qualification_result.rows[current_left_index]
        current_right = self.race.qualification_result.rows[current_right_index]
        tile_width = width//2
        tile_height = 60
        top = 100
        left_2nd_col = tile_width

        if first_to_last:
            if current_left_index >= 2:
                previous_left = self.race.qualification_result.rows[current_left_index-2]
                previous_right = self.race.qualification_result.rows[current_right_index-2]
            else:
                previous_left = previous_right = None

            if previous_left or previous_right:
                previous = self._generate_blurred_row(previous_left, previous_right, width, 2*tile_height, tile_width, tile_height)
                previous_pos = paste(previous, img, left=0, top=top)
                top = previous_pos.bottom
        elif current_left.position > 2:
            empty_spots = self._generate_empty_spots(current_left.position-2, tile_width, tile_height, max_spots=2)
            empty_pos = paste(empty_spots, img, top=top, left=0)
            top = empty_pos.bottom

        current_left_img = self._generate_middle_tile(current_left, tile_width, tile_height)
        cl_pos = paste(current_left_img, img, left=0, top=top)
        top = cl_pos.bottom

        current_right_img = self._generate_middle_tile(current_right, tile_width, tile_height)
        cr_pos = paste(current_right_img, img, left=left_2nd_col, top=top)
        top = cr_pos.bottom

        if first_to_last:
            empty_spots = self._generate_empty_spots(current_right.position+1, tile_width, tile_height)
            paste(empty_spots, img, top=top, left=0)
        else:
            for i in range(current_right.position, 20, 2):
                left = self.race.qualification_result.rows[i]
                right = self.race.qualification_result.rows[i+1]
                if left or right:
                    next = self._generate_blurred_row(left, right, width, 2*tile_height, tile_width, tile_height)
                    next_pos = paste(next, img, left=0 if i % 2 == 0 else tile_width, top=top)
                    top = next_pos.bottom

        title = text_hi_res('Grille'.upper(), (255, 255, 255), FontFactory.black(20), width, 100)
        paste(title, img, top=15)
        return img

    def _generate_empty_spots(self, initial_position, tile_width, tile_height, max_spots=4):
        img = Image.new('RGBA', (tile_width*2, tile_height*max_spots), (0,0,0,0))
        empty = RaceRankingRow(position=initial_position, pilot_name=None, split=None)
        empty_spots = 0
        i = initial_position
        top = 0
        while i <= 20 and empty_spots < 4:
            left = 0 if i % 2 == 1 else tile_width
            empty.position = i
            top = self._paste_row(img, empty, tile_width, tile_height, left=left, top=top)
            empty_spots += 1
            i+=1
        return img

    def _generate_blurred_row(self, left: RaceRankingRow, right:RaceRankingRow, width:int, height:int, tile_width:int, tile_height:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        if left:
            top = self._paste_row(img, left, tile_width, tile_height)
        else:
            top = tile_height
        if right:
            self._paste_row(img, right, tile_width, tile_height, left=tile_width, top=top)
        return img

    def _paste_row(self, img:PngImageFile, row:RaceRankingRow, tile_width:int, tile_height:int, left=0, top=0) -> int:
        tile = self._generate_middle_tile(row, tile_width, tile_height)
        paste(self._get_blurring_img(tile_width, tile_height), tile)
        position = paste(tile, img, left=left, top=top)
        return position.bottom

    def _get_blurring_img(self, width: int, height:int):
        return Image.new('RGBA', (width, height), (100,100,100,15))

    def _generate_middle_tile(self, row: RaceRankingRow, width:int, height:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        grey_line = Image.new('RGB', (width, 3), (100,100,100))
        bg = gradient(Image.new('RGB', (width, height-10), (150,150,150)), GradientDirection.DOWN_TO_UP)
        paste(grey_line, bg, top=height-10)
        paste(bg, img, top=0)
        trigram_height = 30
        trigram_width = 75
        padding_position_trigram = 5
        position_height = height-trigram_height-padding_position_trigram
        postr = str(row.position)
        position_width = width//(8 if len(postr) == 1 else 4)
        position_img = text_hi_res(postr, (255, 255, 255), FontFactory.bold(20), position_width, position_height)
        position_pos = paste(position_img, img, top=0)

        if row.pilot:
            tmp = row.pilot.get_trigram_image(trigram_width, trigram_height)
            paste(tmp, img, top=position_pos.bottom+padding_position_trigram)
        return img
