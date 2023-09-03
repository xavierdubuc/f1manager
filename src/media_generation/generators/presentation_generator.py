from PIL import Image
from ..font_factory import FontFactory
from ..generators.abstract_generator import AbstractGenerator

from ..helpers.transform import *
import textwrap


class PresentationGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'presentation'

    def _generate_basic_image(self) -> PngImageFile:
        width = self.visual_config['width']
        height = self.visual_config['height']
        img = Image.new('RGB', (width, height), (255, 255, 255))

        bg = self._get_background_image()
        if bg:
            with bg:
                paste(bg.convert('RGB'),img)

        return img

    def _add_content(self, final: PngImageFile):
        vertical_padding = 20
        left_width = int(0.67 * final.width)
        initial_top = self._get_visual_title_height()+vertical_padding
        race_title = self._get_race_title_image(left_width, 180)
        race_title_pos = paste(
            race_title, final, left=0,
            top=initial_top
        )

        left_height = final.height - race_title_pos.bottom + vertical_padding
        h_padding = -100
        left_img = self._get_left_content_image(left_width, left_height)
        left_pos = paste(
            left_img, final, left=0, top=race_title_pos.bottom+vertical_padding
        )

        right_width = final.width - h_padding - left_width
        right_top_img = self._get_right_top_content_image(final.width - left_width, race_title.height)
        paste(right_top_img, final, left=left_pos.right, top=initial_top)

        right_img = self._get_right_content_image(right_width, final.height)
        paste(right_img, final, left=left_pos.right + h_padding, top=race_title_pos.bottom)

    def _get_title_lines_image(self, width:int, height:int):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # -------- 200
        #         \
        #      280 \__________
        line_width = 5
        bottom = height - line_width
        fill = (255, 0, 0)

        # horizontal top line
        draw.line(((0, 0), (200, 0)), fill=fill, width=line_width)
        # oblic line
        draw.line(((200, 0), (280, bottom)), fill=fill, width=line_width)
        # horizontal bottom line
        draw.line(((280, bottom), (width, bottom)), fill=fill, width=line_width)
        return img

    def _get_race_title_image(self, width:int, height:int):
        race = self.config.race
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        lines_image = self._get_title_lines_image(width, height)
        paste(lines_image, img)

        day_color = (210, 210, 210)
        day_font = FontFactory.regular(50)
        month_color = (200, 0, 0)
        month_font = FontFactory.regular(60)
        name_color = (200, 0, 0)
        name_font = FontFactory.black(70)

        #  80 - 280
        day = text(str(race.day), day_color, day_font)
        month = text(race.month, month_color, month_font)

        day_pos = paste(day, img, left = (280 - day.width) // 2, top=35)
        paste(month, img, left = (280 - month.width) // 2, top=day_pos.bottom+10)

        circuit = self.config.race.circuit
        with self.config.race.circuit.get_flag() as flag:
            flag = resize(flag, 200, 200)
            flag_pos = paste(flag, img, left=300)
        circuit_img = circuit.get_full_name_img(
            width-flag_pos.right,
            height,
            name_font=name_font,
            name_color=name_color,
            city_font=FontFactory.black(60)
        )
        paste(circuit_img, img, left=flag_pos.right+30)

        return img

    def _get_left_content_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        left_padding = 40

        # photo
        img_top = 20
        remaining_height = height - img_top
        with self.config.race.circuit.get_photo() as photo:
            photo = resize(photo, width-left_padding, remaining_height)
            paste_rounded(img, photo, (left_padding, img_top))

        padding_photo_txt = -100
        top = photo.height+padding_photo_txt-40
        size = photo.height+padding_photo_txt
        bg = Image.new('RGB', (width, size), (80, 80, 80))
        alpha = Image.linear_gradient('L').rotate(-90).resize((bg.width, bg.height))
        alpha = alpha.crop(((alpha.width//4, 0, alpha.width, alpha.height))).resize((alpha.width, alpha.height))
        bg.putalpha(alpha)
        paste(bg, img, left_padding, top)

        # TEXT
        text_font = FontFactory.regular(32)
        text_lines = textwrap.wrap(self.config.description, width=67)

        for text_line in text_lines:
            top += 45
            draw.text((left_padding+20,  top), text_line, 'white', text_font)

        return img

    def _get_right_top_content_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        with Image.open('assets/twitch.png') as twitch_logo :
            twitch_name = text('FBRT_ECHAMP', (255,255,255), FontFactory.black(50), stroke_fill=(145,70,255), stroke_width=4)
            left = width-twitch_name.width-40
            tw_name_pos = paste(twitch_name, img, left=left, top=25)
            hour_img = text(self.config.race.hour, (255, 255, 255), FontFactory.black(50), stroke_fill=(145,70,255), stroke_width=4)
            paste(hour_img, img, left=left, top=tw_name_pos.bottom + 10)

            twitch_logo = resize(twitch_logo, width, int(2*(height/3)))
            paste(twitch_logo, img, left=tw_name_pos.left - 20 - twitch_logo.width)
        return img

    def _get_right_content_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        left = 120

        title_color = (230, 0, 0)
        value_color = (255, 255, 255)
        title_font = FontFactory.regular(32)
        value_font = FontFactory.bold(32)

        with self.config.race.circuit.get_map() as map:
            map = resize(map, width-(left+10), height)
            prev_pos = paste(map, img, top=0, left=(left-10))

        race_length_label = text('Distance totale', title_color, title_font)
        race_length_value = text(f'{self.config.race.get_total_length()} Km', value_color, value_font)

        lap_length_label = text('Longueur', title_color, title_font)
        lap_length_value = text(f'{self.config.race.circuit.lap_length} Km', value_color, value_font)

        lap_amount_label = text('Nombre de tours', title_color, title_font)
        lap_amount_value = text(f'{self.config.race.laps}', value_color, value_font)

        best_lap_label = text('Meilleur temps', title_color, title_font)
        best_lap_value = text(f'{self.config.race.circuit.fbrt_best_lap.lap_time}', value_color, value_font)
        best_lap_author_value = text(
            f'{self.config.race.circuit.fbrt_best_lap.pilot_name} (Saison {self.config.race.circuit.fbrt_best_lap.season})',
            value_color, value_font
        )

        right = width-40
        vertical_padding = 40
        line_padding = 15
        line_color = (255,255,255)
        line_step = 2
        line_space = 10
        line_height_offset = 5

        top = prev_pos.bottom+vertical_padding//2
        prev_pos = paste(race_length_label, img, top=top, left = left)
        paste(race_length_value, img, top=top, left = right - race_length_value.width)
        line_top = top + race_length_label.height - line_height_offset - (race_length_label.height - race_length_value.height)
        draw_horizontal_dotted_line(img, ((prev_pos.right+line_padding, line_top), (right - race_length_value.width-line_padding, line_top)), line_color, step=line_step, space=line_space)

        top = prev_pos.bottom+vertical_padding
        prev_pos = paste(lap_amount_label, img, top=top, left = left)
        paste(lap_amount_value, img, top=top, left = right - lap_amount_value.width)
        line_top = top + lap_amount_label.height - line_height_offset - (lap_amount_label.height - lap_amount_value.height)
        draw_horizontal_dotted_line(img, ((prev_pos.right+line_padding, line_top), (right - lap_amount_value.width-line_padding, line_top)), line_color, step=line_step, space=line_space)

        top = prev_pos.bottom+vertical_padding
        prev_pos = paste(lap_length_label, img, top=top, left = left)
        paste(lap_length_value, img, top=top, left = right - lap_length_value.width)
        line_top = top + lap_length_label.height - line_height_offset - (lap_length_label.height - lap_length_value.height)
        draw_horizontal_dotted_line(img, ((prev_pos.right+line_padding, line_top), (right - lap_length_value.width-line_padding, line_top)), line_color, step=line_step, space=line_space)

        top = prev_pos.bottom+vertical_padding
        prev_pos = paste(best_lap_label, img, top=top, left = left)
        paste(best_lap_value, img, top=top, left = right - best_lap_value.width)
        line_top = top + best_lap_label.height - line_height_offset - (best_lap_label.height - best_lap_value.height)
        draw_horizontal_dotted_line(img, ((prev_pos.right+line_padding, line_top), (right - best_lap_value.width-line_padding, line_top)), line_color, step=line_step, space=line_space)

        top = int(prev_pos.bottom+(vertical_padding/2))
        paste(best_lap_author_value, img, top=top, left=right - best_lap_author_value.width)
        return img
