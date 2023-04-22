from PIL import Image
from ..font_factory import FontFactory
from ..generators.abstract_generator import AbstractGenerator

from ..helpers.transform import *
import textwrap

class PresentationGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'presentation'

    def _generate_basic_image(self) -> PngImageFile:
        with Image.open('assets/bg.png') as original_bg:
            base = original_bg.copy().convert('RGB')
            # BG
            bg = Image.new('RGB', (base.width, base.height), (150, 150, 150))
            alpha = Image.linear_gradient('L').rotate(-90).resize((base.width, base.height))
            alpha = alpha.crop(((0, 0, base.width//2, base.height))).resize((base.width, base.height))
            base.paste(bg, alpha)
        return base

    def _add_content(self, final: PngImageFile):
        title_height = self._get_visual_title_height()

        right_part_width = int(3.5 * (final.width / 10))
        padding_between = int(0.5 * (final.width / 10))
        left_content_height = final.height - title_height 
        left_part_width = final.width - right_part_width - padding_between
        right_part_left = final.width - right_part_width
        right_part_top = title_height + 100
        right_part_height = final.height - right_part_top

        # get race title

        left_content = self._get_left_content_image(left_part_width, left_content_height)
        right_top_content = self._get_right_top_content_image(right_part_width, 100)
        right_content = self._get_right_content_image(right_part_width, right_part_height)
        final.paste(left_content, (0, title_height), left_content)
        final.paste(right_content, (right_part_left, right_part_top), right_content)
        final.paste(right_top_content, (right_part_left, title_height), right_top_content)

    def _get_left_content_image(self, width:int, height:int):
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))

        month_color = (50, 50, 50)
        title_color = (50, 50, 50)
        day_color = (210, 210, 210)
        text_font = FontFactory.regular(32)
        hour_font = FontFactory.bold(40)
        day_font = FontFactory.regular(50)
        month_font = FontFactory.regular(60)
        title_font_size = 80
        title_font = FontFactory.bold(title_font_size)

        padding_h = 75
        padding_v = 20
        padding_between_dates = 20
        line_width = 5

        draw = ImageDraw.Draw(img)
        _, _, day_width, day_height = draw.textbbox((0, 0), f'{self.config.race.day}.', day_font)
        _, _, date_width, date_height = draw.textbbox((0, 0), self.config.race.month, month_font)

        date_bottom = line_width+padding_v+day_height+padding_between_dates+date_height+padding_v
        month_with_padding_right = date_width + 2 * padding_h
        day_right = padding_h+date_width
        day_left = (month_with_padding_right - day_width) // 2
        month_left = (month_with_padding_right - date_width) // 2

        # Title BG
        bg = Image.new('RGB', (width, date_bottom), (100, 100, 100))
        alpha = Image.linear_gradient('L').rotate(-90).resize((width, date_bottom))
        bg.putalpha(alpha)
        img.paste(bg)

        # horizontal top line
        draw.line(((0,0), (day_right, 0)), fill=(255, 0, 0), width=line_width)

        # day
        draw.text((day_left, padding_v), f'{self.config.race.day}.', day_color, day_font)

        # month
        draw.text((month_left, padding_v + day_height + padding_between_dates), self.config.race.month, month_color, month_font)

        # oblic line
        draw.line(((day_right, 0), (month_with_padding_right, date_bottom)), fill=(255, 0, 0), width=line_width)

        # horizontal bottom line
        hbline_right = width - padding_h
        draw.line(((month_with_padding_right-1, date_bottom), (hbline_right, date_bottom)), fill=(255, 0, 0), width=line_width)

        # circuit name
        padding_before_circuit_name = 40
        name_top = ((date_bottom - title_font_size) // 2) - 3
        name_left = month_with_padding_right + padding_before_circuit_name
        draw.text((name_left, name_top), self.config.race.circuit.name, title_color, title_font)

        # circuit flag
        with Image.open(f'assets/circuits/flags/{self.config.race.circuit.id}.png') as flag:
            flag.thumbnail((200,200), Image.Resampling.LANCZOS)
            img.paste(flag, (hbline_right - flag.width, (date_bottom - flag.height)//2), flag)

        # photo
        img_top = date_bottom + 20
        remaining_height = height - img_top
        with Image.open(f'assets/circuits/photos/{self.config.race.circuit.id}.png') as photo:
            photo = resize(photo, width-month_left, remaining_height)
            paste_rounded(img, photo, (month_left, img_top))

        # hour
        _, _, hour_width, hour_height = draw.textbbox((0, 0), self.config.race.hour, hour_font)
        hour_h_padding = 40
        hour_v_padding = 20
        hour_top = img_top + photo.height - hour_height - 2 * hour_v_padding
        bg_size = (hour_width + 2 * hour_h_padding, hour_height + 2 * hour_v_padding)

        # hour bg
        bg_hour = Image.new('RGB', bg_size, (0, 0, 0))
        gradient(bg_hour, GradientDirection.LEFT_TO_RIGHT)
        img.alpha_composite(bg_hour, (month_left, hour_top))
        # hour line
        draw.line(((month_left+4, hour_top), (month_left+4, hour_top+bg_hour.height-1)), fill=(32, 167, 215), width=10)
        # hour text
        draw.text((month_left+hour_h_padding, hour_top+hour_v_padding), self.config.race.hour, color=day_color, font=hour_font)

        # TEXT
        text_lines = textwrap.wrap(self.config.description, width=58)
        top = hour_top+hour_v_padding+70
        for text_line in text_lines:
            draw.text((month_left,  top), text_line, 'white', text_font)
            top += 40

        return img

    def _get_right_content_image(self, width:int, height:int):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        inf_img = self.config.race.get_just_information_image(width, height, FontFactory.regular(34))
        img.alpha_composite(inf_img)
        return img

    def _get_right_top_content_image(self, width: int, height: int):
        img = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        with Image.open('assets/twitch.png') as twitch_logo :
            twitch_name = text('FBRT_ECHAMP', (255,255,255), FontFactory.black(50), stroke_fill=(145,70,255), stroke_width=4)
            left = width-twitch_name.width-40
            tw_name_pos = paste(twitch_name, img, left=left, use_obj=True)

            twitch_logo = resize(twitch_logo, width, twitch_name.height)
            paste(twitch_logo, img, left=tw_name_pos.left - 20 - twitch_logo.width, use_obj=True)
        return img

