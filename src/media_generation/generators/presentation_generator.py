from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngImageFile
from src.media_generation.data import RESERVIST_TEAM
from src.media_generation.generators.abstract_race_generator import AbstractRaceGenerator
from src.media_generation.models.pilot import Pilot
from src.media_generation.readers.race_reader_models import race

from ..font_factory import FontFactory

from ..helpers.transform import *
import textwrap


class PresentationGenerator(AbstractRaceGenerator):
    def _get_visual_type(self) -> str:
        return 'presentation'

    def _generate_basic_image(self) -> PngImageFile:
        img = super()._generate_basic_image()
        lines = self.visual_config.get('lines', [])
        if lines:
            draw = ImageDraw.Draw(img)
            for line in lines:
                draw.line(line['coordinates'], line['color'], line['thickness'])
        return img

    def _add_content(self, base_img: PngImageFile):
        self._render_date(base_img)
        self._render_headline(base_img)
        self._render_circuit_image(base_img)
        self._render_circuit_location(base_img)
        self._render_circuit_details(base_img)
        self._render_race_round(base_img)
        self._render_fastest_lap(base_img)
        self._render_last_winner(base_img)
        self._render_logos(base_img)
        self._render_description(base_img)

    def _render_date(self, base_img:PngImageFile):
        config = self.visual_config.get('date', {})
        w = config.get('width')
        h = config.get('height')
        content = f"{self.race.full_date.day} {month_fr(self.race.full_date.month-1)}, {self.race.hour}"
        date_img = text_hi_res(content, config.get('font_color', (255, 255, 255)),
                    FontFactory.regular(40), w, h)
        self.paste_image(date_img, base_img, config)

    def _render_headline(self, base_img:PngImageFile):
        config = self.visual_config.get('headline', {})
        font = FontFactory.get_font(config.get('font'), 40, FontFactory.regular)
        for part_config in config.get('parts'):
            w = part_config.get('width')
            h = part_config.get('height')
            color = part_config.get('font_color', (255, 255, 255))
            part_img = text_hi_res(part_config.get('content'), color, font, w, h)
            self.paste_image(part_img, base_img, part_config)

    def _render_circuit_image(self, base_img:PngImageFile):
        config = self.visual_config.get('image', {})
        w = config.get('width')
        h = config.get('height')
        with self.race.circuit.get_partial_photo(w,h) as photo:
            self.paste_image(photo, base_img, config)

    def _render_circuit_details(self, base_img:PngImageFile):
        config = self.visual_config.get('map', {})
        with self.race.circuit.get_map() as map:    
            map = resize(map, config.get('width', 200), config.get('height', 200))
            self.paste_image(map, base_img, config)

        lap_config = self.visual_config.get('laps')
        laps_w = lap_config.get('width', 200)
        laps_h = lap_config.get('height', 30)
        laps_img = Image.new('RGBA', (laps_w, laps_h), (0,0,0,0))
        laps_content = lap_config.get('content', '{lap}').format(lap=self.race.laps)
        laps_txt = self.text(lap_config.get('text'), laps_content, default_font=FontFactory.regular)
        self.paste_image(laps_txt, laps_img, lap_config.get('text'))
        self.paste_image(laps_img, base_img, lap_config)

        length_config = self.visual_config.get('length')
        length_w = length_config.get('width', 200)
        length_h = length_config.get('height', 30)
        length_img = Image.new('RGBA', (length_w, length_h), (0,0,0,0))
        length_content = length_config.get('content', '{length}').format(length=self.race.circuit.lap_length)
        length_txt = self.text(length_config.get('text'), length_content, default_font=FontFactory.regular)
        self.paste_image(length_txt, length_img, length_config.get('text'))
        self.paste_image(length_img, base_img, length_config)

        total_length_config = self.visual_config.get('total_length')
        total_length_w = total_length_config.get('width', 200)
        total_length_h = total_length_config.get('height', 30)
        total_length_img = Image.new('RGBA', (total_length_w, total_length_h), (0,0,0,0))
        total_length_content = total_length_config.get('content', '{total_length}').format(total_length=self.race.get_total_length())
        total_length_txt = self.text(total_length_config.get('text'), total_length_content, default_font=FontFactory.regular)
        self.paste_image(total_length_txt, total_length_img, total_length_config.get('text'))
        self.paste_image(total_length_img, base_img, total_length_config)

    def _render_circuit_location(self, base_img:PngImageFile):
        config = self.visual_config.get('location', {})
        flag_config = config.get('flag', {})
        flag_w = flag_config.get('width', 100)
        flag_h = flag_config.get('height', 100)
        with self.race.circuit.get_flag() as flag_img:
            flag_img = resize(flag_img, flag_w, flag_h)
        self.paste_image(flag_img, base_img, flag_config)

        name_config = config.get('name', {})
        name_content = f'{self.race.circuit.city}'.upper()
        name_img = text_hi_res(
            name_content, name_config.get('font_color', (255,255,255)),
            FontFactory.regular(40),
            name_config.get('width', 500), name_config.get('height', 40),
        )
        self.paste_image(name_img, base_img, name_config)

    def _render_race_round(self, base_img:PngImageFile):
        config = self.visual_config.get('round', {})
        race_round = self.race.round
        amount_of_races = self.championship_config['seasons'][self.season]['amount_of_races']
        content = config.get('content', '{i}/{tot}').format(i=race_round, tot=amount_of_races)
        img = text_hi_res(
            content, config.get('font_color', (255,255,255)),
            FontFactory.regular(40),
            config.get('width', 240), config.get('height', 40),
        )
        self.paste_image(img, base_img, config)

    def _render_last_winner(self, base_img:PngImageFile):
        config = self.visual_config.get('last_winner', {})
        w = config.get('width')
        h = config.get('height')
        img = Image.new('RGBA', (w,h), (0,0,0,0))

        pilot_config = config.get('pilot', {})
        pilot_name = self.race.circuit_last_winner_name
        pilot = self.config.pilots.get(pilot_name) or Pilot(name='?', team=RESERVIST_TEAM)
        pilot_img = pilot.get_mid_range_image(pilot_config.get('width'), pilot_config.get('height'))        
        self.paste_image(pilot_img, img, pilot_config)

        # PILOT NAME + TITLE
        text_config = config.get('text', {})
        text_w = text_config.get('width', w)
        text_h = text_config.get('height', h)
        bgcolor = text_config.get('background', (30, 30, 30, 235))
        text_img = Image.new('RGBA', (text_w, text_h), bgcolor)

        # PILOT NAME
        pilot_name_config = text_config.get('name', {})
        pilot_name_w = pilot_name_config.get('width', w)
        pilot_name_h = pilot_name_config.get('height', h)
        pilot_name_color = text_config.get('font_color', (30,30,30))
        pilot_name_font = FontFactory.black(40)
        pilot_name_txt = text_hi_res(pilot_name, pilot_name_color, pilot_name_font, pilot_name_w, pilot_name_h, use_background=bgcolor)
        self.paste_image(pilot_name_txt, text_img, pilot_name_config)

        # TITLE
        title_config = text_config.get('title', {})
        title_w = title_config.get('width', w)
        title_h = title_config.get('height', h)
        title_color = text_config.get('font_color', (30,30,30))
        title_font = FontFactory.regular(40)
        title_content = title_config.get('content', 'Dernier vainqueur')
        title_txt = text_hi_res(title_content, title_color, title_font, title_w, title_h, use_background=bgcolor)
        self.paste_image(title_txt, text_img, title_config)

        # SEASON
        season_config = text_config.get('season', {})
        season_w = season_config.get('width', w)
        season_h = season_config.get('height', h)
        season_color = text_config.get('font_color', (30,30,30))
        season_font = FontFactory.regular(40)
        season_content = season_config.get('content', '{season}').format(season=self.config.race.circuit_last_winner_season)
        season_txt = text_hi_res(season_content, season_color, season_font, season_w, season_h, use_background=bgcolor)
        self.paste_image(season_txt, text_img, season_config)

        self.paste_image(text_img, img, text_config)
        self.paste_image(img, base_img, config)

    def _render_fastest_lap(self, base_img:PngImageFile):
        config = self.visual_config.get('fastest_lap')
        w = config.get('width')
        h = config.get('height')
        img = Image.new('RGBA', (w,h), (0,0,0,0))

        pilot_name = self.race.circuit_fastest_lap_pilot_name
        lap_time = self.race.circuit_fastest_lap_time
        if not lap_time or not pilot_name:
            return

        # PILOT IMG
        pilot_config = config.get('pilot')
        pilot = self.config.pilots.get(pilot_name) or Pilot(name='?', team=RESERVIST_TEAM)
        pilot_img = pilot.get_mid_range_image(pilot_config.get('width'), pilot_config.get('height'))
        self.paste_image(pilot_img, img, pilot_config)

        # PILOT NAME + TITLE
        text_config = config.get('text', {})
        text_w = text_config.get('width', w)
        text_h = text_config.get('height', h)
        bgcolor = text_config.get('background', (30, 30, 30, 235))
        text_img = Image.new('RGBA', (text_w, text_h), bgcolor)

        # PILOT NAME
        pilot_name_config = text_config.get('name', {})
        pilot_name_w = pilot_name_config.get('width', w)
        pilot_name_h = pilot_name_config.get('height', h)
        pilot_name_color = text_config.get('font_color', (30,30,30))
        pilot_name_font = FontFactory.black(40)
        pilot_name_txt = text_hi_res(pilot_name, pilot_name_color, pilot_name_font, pilot_name_w, pilot_name_h, use_background=bgcolor)
        self.paste_image(pilot_name_txt, text_img, pilot_name_config)

        # TITLE
        title_config = text_config.get('title', {})
        title_w = title_config.get('width', w)
        title_h = title_config.get('height', h)
        title_color = text_config.get('font_color', (30,30,30))
        title_font = FontFactory.regular(40)
        title_content = title_config.get('content', 'Dernier vainqueur')
        title_txt = text_hi_res(title_content, title_color, title_font, title_w, title_h, use_background=bgcolor)
        self.paste_image(title_txt, text_img, title_config)

        self.paste_image(text_img, img, text_config)

        # TIME
        time_config = config.get('time', {})
        time_w = time_config.get('width', w)
        time_h = time_config.get('height', h)
        bgcolor = time_config.get('background', (30, 30, 30, 235))
        time_img = Image.new('RGBA', (time_w, time_h), bgcolor)

        # FASTEST LAP IMG
        with Image.open(f'assets/fastest_lap.png') as icon:
            icon = resize(icon, time_h, time_h)
            paste(icon, time_img, left=0)

        # LAP TIME
        lap_config = time_config.get('lap', {})
        lap_w = lap_config.get('width', w)
        lap_h = lap_config.get('height', h)
        lap_color = time_config.get('font_color', (30,30,30))
        lap_font = FontFactory.black(40)
        lap_txt = text_hi_res(lap_time, lap_color, lap_font, lap_w, lap_h, use_background=bgcolor)
        self.paste_image(lap_txt, time_img, lap_config)

        # SEASON
        if season := self.race.circuit_fastest_lap_season:
            season_config = time_config.get('season', {})
            season_content = season_config.get('content', '{season}').format(season=season)
            season_w = season_config.get('width', w)
            season_h = season_config.get('height', h)
            season_color = time_config.get('font_color', (30,30,30))
            season_font = FontFactory.regular(20)
            season_txt = text_hi_res(season_content, season_color, season_font, season_w, season_h, use_background=bgcolor)
            self.paste_image(season_txt, time_img, season_config)

        self.paste_image(time_img, img, time_config)
        self.paste_image(img, base_img, config)

    def _render_logos(self, base_img:PngImageFile):
        # TWITCH
        twitch_config = self.visual_config.get('twitch', {})
        twitch_w = twitch_config.get('width', 250)
        twitch_h = twitch_config.get('height', 100)
        twitch_bg = twitch_config.get('background', (145, 70, 255))
        twitch_img = Image.new('RGB', (twitch_w, twitch_h), twitch_bg)
        with Image.open('assets/twitch.png') as twitch_logo :
            logo_config = twitch_config.get('logo')
            twitch_logo = resize(twitch_logo, height=twitch_h)
            self.paste_image(twitch_logo, twitch_img, logo_config)

            name_config = twitch_config.get('name')
            name_font = FontFactory.black(name_config.get('font_size'))
            twitch_name = text('FBRT_ECHAMP', (255,255,255), name_font)
            self.paste_image(twitch_name, twitch_img, name_config)

            hour_config = twitch_config.get('hour')
            hour_font = FontFactory.black(hour_config.get('font_size'))
            hour_img = text(self.race.hour, (255, 255, 255), hour_font)
            self.paste_image(hour_img, twitch_img, hour_config)
        self.paste_image(twitch_img, base_img, twitch_config)

        for logo_config in self.visual_config.get('logos'):
            with Image.open(logo_config['path']) as logo_img:
                logo_width = logo_config.get('width', 100)
                logo_height = logo_config.get('height', 100)
                logo_img = resize(logo_img, height=logo_height, width=logo_width)
                self.paste_image(logo_img, base_img, logo_config)

    def _render_description(self, base_img:PngImageFile):
        # TEXT
        description_config = self.visual_config.get('description', {})
        w = description_config.get("width", 200)
        h = description_config.get("height", 200)
        img = Image.new('RGBA', (w,h), (0,0,0,0))
        chars_by_line = description_config.get('chars_by_line', 54)
        text_lines = textwrap.wrap(self.race.presentation_text, width=chars_by_line)
        line_height = description_config.get('line_height', 30)

        top = 0
        for text_line in text_lines:
            text = self.text(description_config, text_line)
            top += line_height
            paste(text, img, top=top)

        self.paste_image(img, base_img, description_config)
        return img
