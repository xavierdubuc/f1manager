import logging
from typing import List

from moviepy.editor import *
from PIL import Image
from PIL.PngImagePlugin import PngImageFile

from src.media_generation.font_factory import FontFactory
from src.media_generation.generators.exceptions import IncorrectDataException
from src.media_generation.models.ranking_row_renderer import RankingRowRenderer
from src.media_generation.readers.race_reader_models.race_ranking import RaceRankingRow

from ..helpers.generator_config import GeneratorConfig
from ..helpers.transform import paste, text, text_size
from ..models import Pilot

_logger = logging.getLogger(__name__)


class GridRibbonGenerator:
    def __init__(self, championship_config: dict, config:GeneratorConfig, season: int, identifier: str = None):
        self.championship_config = championship_config
        self.config = config
        self.race = config.race
        self.season = season
        self.visual_config = self.championship_config['settings']['visuals'].get('grid_ribbon', {})
        self.width = 1920
        self.height = 60
        self.font_size = 30
        self.font = FontFactory.regular(self.font_size)
        self.tmp_dir = './output/grid_ribbon_elements'
        self.force_regenerate = True

    def generate(self):
        title_width = 520
        start_position = title_width + 150
        space_between_position = 50
        base_img_path, _ = self._get_base_image()
        title_img_path, _ = self._get_title_image(title_width)
        title_mask_path, _ = self._get_title_mask(title_width)
        ranking = self.race.qualification_result
        i = 1
        grid_images = []
        for row in ranking.rows:
            img = self._get_grid_image(i, row)
            if row.pilot != None and img != None:
                grid_images.append(img)
            i += 1

        if len(grid_images) == 0:
            raise IncorrectDataException('Ranking is empty, won\'t generate !')
        bg_clip = ImageClip(base_img_path)
        # speed 75 --> duration_by_driver = 6
        # speed 125 --> duration_by_driver = 4
        speed = 75
        duration_by_driver = 6
        duration = len(grid_images) * duration_by_driver
        bg_clip = bg_clip.set_duration(duration)
        title_clip = ImageClip(title_img_path)
        title_clip = title_clip.set_duration(duration)
        title_clip = title_clip.set_position(lambda t: (0, 'center'))
        title_mask = ImageClip(title_mask_path, ismask=True)

        grid_clips = []
        for grid_img_path, grid_img in grid_images:
            grid_clip = ImageClip(grid_img_path)
            grid_clip = grid_clip.set_duration(duration)

            def _position(start_position):
                return lambda t: (start_position - speed * t, 'center')
            grid_clip = grid_clip.set_position(_position(start_position))
            grid_clips.append(grid_clip)
            start_position += grid_img.width + space_between_position

        final = CompositeVideoClip(
            [bg_clip, title_clip] + grid_clips + [title_clip.set_mask(title_mask)],
        )
        filename = f'{self.config.output}.mp4'
        final.write_videofile(filename, fps=24)

        return filename

    def _get_grid_image(self, pos, ranking_row: RaceRankingRow) -> PngImageFile:
        if not ranking_row or not ranking_row.pilot:
            return None
        row_renderer = RankingRowRenderer(
            ranking_row,
            self.championship_config['settings']['components']['ranking_row_renderer']
        )
        font = FontFactory.regular(30)
        fg_color = (255, 255, 255)

        def _generate():
            pos_img = row_renderer._get_position_image()
            estimated_logo_width = 50
            padding = 20
            estimated_name_width = text_size(ranking_row.pilot.name.upper(), font)[0]
            width = estimated_logo_width + estimated_name_width + pos_img.width + padding * 2
            pilot_img = ranking_row.pilot.get_ranking_image(width, self.height, font, True, fg_color)
            img = Image.new('RGBA', (pos_img.width+pilot_img.width+padding, self.height))
            pos_pos = paste(pos_img, img, left=0)
            paste(pilot_img, img, pos_pos.right+padding)
            return img
        return self._get_image_or_generate(f'grid_{pos}.png', _generate)

    def _get_base_image(self) -> PngImageFile:
        bg_color = (0, 0, 0)

        def _generate():
            return Image.new('RGB', (self.width, self.height), bg_color)
        return self._get_image_or_generate('bg.png', _generate)

    def _get_title_image(self, width) -> PngImageFile:
        color = (255, 255, 255)
        txt = 'Résultats qualifications'.upper()

        def _generate():
            img = Image.new('RGBA', (width, self.height), (0, 0, 0, 0))
            txt_img = text(txt, color, self.font)
            paste(txt_img, img)
            return img
        return self._get_image_or_generate('title.png', _generate)

    def _get_title_mask(self, width) -> PngImageFile:
        def _generate():
            return Image.new('RGB', (width, self.height), (255, 255, 255))
        return self._get_image_or_generate('title_mask.png', _generate)

    ## PRIVATE

    def _get_image_or_generate(self, filename: str, generate_fct: callable):
        filepath = os.path.join(self.tmp_dir, filename)
        if os.path.exists(filepath) and not self.force_regenerate:
            with Image.open(filepath) as img:
                return filepath, img.copy()
        else:
            img = generate_fct()
            img.save(filepath, quality=95)
            return filepath, img