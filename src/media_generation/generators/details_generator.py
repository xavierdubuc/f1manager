from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngImageFile
from ..helpers.transform import *
from ..models import PilotResult

from ..font_factory import FontFactory
from ..generators.abstract_generator import AbstractGenerator

small_font = FontFactory.regular(32)
font = FontFactory.regular(38)
big_font = FontFactory.regular(56)
pilot_font = FontFactory.bold(30)


class DetailsGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'details'

    def _add_content(self, final: PngImageFile):
        title_height = self._get_visual_title_height()
        top_h_padding = 20
        available_width = final.width - 2 * top_h_padding
        subtitle_image = self._get_subtitle_image(available_width, 90)
        subt_dimension = paste(subtitle_image, final, 10, title_height + top_h_padding, use_obj=True)

        rankings_top = subt_dimension.bottom + 30
        rankings_height = final.height - rankings_top
        rankings_img = self._get_ranking_image(final.width, rankings_height)
        final.paste(rankings_img, (0, rankings_top), rankings_img)

    def _get_subtitle_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (0, 0, 0 ,0))
        padding = 20
        race_title_width = int(0.32 * width - padding)

        # race_title_image = self.config.race.get_title_image_simple(race_title_width, height, date_font, race_title_font)
        race_title_image = self.config.race.get_circuit_and_date_img(
            race_title_width,
            height,
            name_font=FontFactory.black(36),
            city_font=FontFactory.black(32),
            date_font=FontFactory.regular(28)
        )
        race_dimension = paste(race_title_image, img, left=padding, use_obj=True)

        fastest_lap_left = race_dimension.right + padding
        fastest_lap_width = width - padding - fastest_lap_left
        fastest_lap_img = self._get_fastest_lap_image(fastest_lap_width, height)
        paste(fastest_lap_img, img, fastest_lap_left)
        return img

    def _get_fastest_lap_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        with Image.open(f'assets/fastest_lap.png') as fstst_img:
            fstst_img = resize(fstst_img, height, height)
            paste(fstst_img, img, 0)

        draw = ImageDraw.Draw(img)
        text_font = FontFactory.bold(40)
        text_content = 'FASTEST LAP'
        _, _, text_width, text_height = draw.textbbox((0, 0), text_content, text_font)

        text_padding = 40
        black_box_width = text_width + 2 * text_padding
        black_box_left = fstst_img.width
        black_bg = Image.new('RGB', (black_box_width, height), (0, 0, 0))
        img.paste(black_bg, (black_box_left, 0))

        text_left = black_box_left + text_padding
        text_top = (height-text_height)//2
        draw.text((text_left, text_top), text_content, (180, 60, 220), text_font)

        pilot_bg_left = (black_box_left + black_box_width)
        pilot_bg_width = width - pilot_bg_left
        pilot_bg = Image.new('RGB', (pilot_bg_width, height), (20, 20, 20))
        alpha = Image.linear_gradient('L').rotate(-90).resize((pilot_bg_width, height))
        pilot_bg.putalpha(alpha)
        img.paste(pilot_bg, (pilot_bg_left, 0))

        pilot_and_lap_padding = 20
        pilot_and_lap_left = pilot_bg_left+pilot_and_lap_padding
        pilot_font = FontFactory.bold(45)
        lap_font = FontFactory.regular(25)
        lap_content = f'Lap {self.config.fastest_lap.lap}'
        _, _, pilot_width, pilot_height = draw.textbbox((0, 0), self.config.fastest_lap.pilot.name, pilot_font)
        _, _, lap_width, lap_height = draw.textbbox((0, 0), lap_content, lap_font)
        space_between_pilot_and_lap = 10
        pilot_and_lap_height = pilot_height + lap_height + space_between_pilot_and_lap
        pilot_top = (height - pilot_and_lap_height) // 2
        lap_top = pilot_top + pilot_height + space_between_pilot_and_lap

        draw.text((pilot_and_lap_left, pilot_top), self.config.fastest_lap.pilot.name, (255, 255, 255), pilot_font)
        draw.text((pilot_and_lap_left + (pilot_width-lap_width), lap_top), lap_content, (255, 255, 255), lap_font)

        time_font = FontFactory.bold(55)
        time_left = pilot_and_lap_left + max(pilot_width, lap_width) + 40
        _, _, time_width, time_height = draw.textbbox((0, 0), self.config.fastest_lap.time, time_font)
        time_top = (height-time_height) // 2
        draw.text((time_left, time_top), self.config.fastest_lap.time, (255, 255, 255), time_font)

        team_left = time_left + time_width + 40
        pilot = self.config.race.get_pilot(self.config.fastest_lap.pilot.name)
        with Image.open(pilot.get_team_image()) as team_img:
            team_img.thumbnail((height, height), Image.Resampling.LANCZOS)
            img.paste(team_img, (team_left, 0), team_img)
        return img

    def _get_ranking_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (30, 30, 30, 235))
        top = 0
        hop_between_position = 38
        row_height = 62
        padding_left = 20
        padding_between = 40
        padding_right = 40
        col_width = (width - (padding_left+padding_between+padding_right)) // 2
        first_col_left = padding_left
        second_col_left = padding_left + col_width + padding_between

        maximum_split_size = 0
        maximum_tyre_amount = 0
        for _, pilot_data in self.config.ranking.iterrows():
            if pilot_data[1] is not None:
                w,_ = text_size(pilot_data[1], small_font)
                if w > maximum_split_size:
                    maximum_split_size = w
            if pilot_data[2] is not None:
                tyre_amount = len(pilot_data[2])
                if tyre_amount > maximum_tyre_amount:
                    maximum_tyre_amount = tyre_amount
        for index, pilot_data in self.config.ranking.iterrows():
            # Get pilot
            pilot_name = pilot_data[0]
            pilot = self.config.race.get_pilot(pilot_name)

            pos = index + 1
            if pilot:
                has_fastest_lap = pilot_name == self.config.fastest_lap.pilot.name
                tyres = pilot_data[2] if isinstance(pilot_data[2], str) else ''
                pilot_result = PilotResult(pilot, pos, pilot_data[1], tyres)

                left = first_col_left if index % 2 == 0 else second_col_left
                pilot_result_image = pilot_result.get_details_image(col_width, row_height, maximum_split_size, maximum_tyre_amount, has_fastest_lap)
                img.paste(pilot_result_image, (left, top))
            top += hop_between_position
        return img
