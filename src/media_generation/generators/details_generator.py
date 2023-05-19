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
        race_title_width = int(0.35 * width - padding)

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
        img = Image.new('RGBA', (width, height), (30, 30, 30, 235))

        # FASTEST LAP IMG
        with Image.open(f'assets/fastest_lap.png') as fstst_img:
            fstst_img = resize(fstst_img, height, height)
            logo_pos = paste(fstst_img, img, left=0, use_obj=True)

        # TEAM LOGO
        pilot = self.config.race.get_pilot(self.config.fastest_lap.pilot.name)
        team = pilot.team
        with team.get_results_logo() as team_img:
            team_img = resize(team_img, height, height)
            team_pos = paste(team_img, img, left=logo_pos.right+20, use_obj=True)

        # PILOT NAME
        pilot_font = FontFactory.bold(45)
        pilot_content = self.config.fastest_lap.pilot.name.upper()
        pilot_txt = text(pilot_content, (255,255,255), pilot_font)
        pilot_pos = paste(pilot_txt, img, left=team_pos.right + 30, use_obj=True)

        # LAP #
        lap_font = FontFactory.regular(30)
        lap_content = f'LAP {self.config.fastest_lap.lap}'
        lap_txt = text(lap_content, (255,255,255), lap_font)
        lap_pos = paste(lap_txt, img, left=pilot_pos.right+30, use_obj=True)

        # LAP TIME
        time_font = FontFactory.bold(45)
        time_txt = text(self.config.fastest_lap.time, (255, 255, 255), time_font)
        time_pos = paste(time_txt, img, left=width-time_txt.width-15, use_obj=True)

        return img

    def _get_ranking_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (30, 30, 30, 235))
        top = 20
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
                is_pilot_of_the_day = pos == 4
                tyres = pilot_data[2] if isinstance(pilot_data[2], str) else ''
                pilot_result = PilotResult(pilot, pos, pilot_data[1], tyres)

                left = first_col_left if index % 2 == 0 else second_col_left
                pilot_result_image = pilot_result.get_details_image(col_width, row_height, maximum_split_size, maximum_tyre_amount, has_fastest_lap, is_pilot_of_the_day)
                img.paste(pilot_result_image, (left, top))
            top += hop_between_position
        return img
