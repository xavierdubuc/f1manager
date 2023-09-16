from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from ..helpers.transform import *

from ..font_factory import FontFactory
from ..generators.abstract_generator import AbstractGenerator

BG_COLOR = (20, 20, 30)

class DriverOfTheDayGenerator(AbstractGenerator):
    def _get_visual_type(self) -> str:
        return 'driver_of_the_day'

    def _generate_title_image(self, base_img: PngImageFile) -> PngImageFile:
        if self.visual_config.get('title_height', 0) == 0:
            return
        return super()._generate_title_image(base_img)

    def _get_visual_title_height(self, base_img: PngImageFile = None) -> int:
        return self.visual_config['title_height']

    def _generate_basic_image(self) -> PngImageFile:
        width = self.visual_config['width']
        height = self.visual_config['height']
        img = Image.new('RGB', (width, height), BG_COLOR)
        return img

    def _add_content(self, final: PngImageFile):
        w,h = final.size

        # CENTER IMAGE
        center_config = self.visual_config['center_rectangle']
        center_left = center_config['left']
        center_top = center_config['top']
        center_img = self._get_center_img(w - (center_left * 2), h - (center_top * 2))
        center_pos = paste(center_img, final, left=center_left, top=center_top)

        # DRIVER OF THE DAY TEXT
        dotd_text_img = self._get_driver_of_the_day_block_text_img(w,h)
        dotd_text_config = self.visual_config['dotd_text']
        dotd_left = dotd_text_config['left']
        dotd_top = dotd_text_config['top']
        paste(dotd_text_img, final, left=dotd_left, top=dotd_top)

        # PILOT IMAGE
        driver = self.config.race.get_pilot(self.config.driver_of_the_day[0])
        pilot_photo = driver.get_long_range_image()
        driver_height = self.visual_config['pilot_photo']['height']
        driver_top = self.visual_config['pilot_photo']['top']
        pilot_photo = resize(pilot_photo, height=driver_height, keep_ratio=True)
        paste(pilot_photo, final, top=driver_top)

        # BOTTOM IMG (HIDE BOTTOM OF PILOT)
        bottom_img = self._get_bottom_image(w, center_top)
        paste(bottom_img, final, left=0, top=h-bottom_img.height)

        # PILOT
        pilot_name_font = FontFactory.black(30)
        pilot_name_img = text(driver.name, (255, 255, 255), pilot_name_font)
        pilot_name_pos = paste(pilot_name_img, final,
              left=center_pos.left+20,
              top=center_pos.bottom-pilot_name_img.height-20)
        with Image.open(driver.team.get_breaking_logo()) as logo:
            logo = resize(logo, 100, 100)
            paste(logo, final, left=center_pos.left + 20,
                  top=pilot_name_pos.top-logo.height - 10)

        # PERCENTAGE TEXT
        percentage_str = self.config.driver_of_the_day[1] or '0%'
        percentage = round(float(percentage_str.replace('%','').replace(',','.')))
        percentage_font = FontFactory.bold(40)
        percentage_sec_font = FontFactory.regular(20)
        percentage_txt_img = text(f'{percentage}%', driver.team.main_color, percentage_font)
        percentage_of_txt_img = text('DES', (255, 255, 255), percentage_sec_font)
        percentage_vote_txt_img = text('VOTES', (255, 255, 255), percentage_sec_font)
        votes_pos = paste(percentage_vote_txt_img, final,
              left=center_pos.right-percentage_vote_txt_img.width-5,
              top=center_pos.bottom-percentage_vote_txt_img.height-5)
        of_pos = paste(percentage_of_txt_img, final,
              left=votes_pos.left,
              top=votes_pos.top-percentage_of_txt_img.height)
        paste(percentage_txt_img, final,
              left=votes_pos.left-percentage_txt_img.width-2,
              top=of_pos.top-1)

    def _get_bottom_image(self, w:int, h:int) -> PngImageFile:
        img = Image.new('RGB', (w,h), BG_COLOR)
        circuit = self.config.race.circuit
        with circuit.get_flag() as f:
            f = resize(f, height=h//4)
            flag_pos = paste(f, img, left=20)
        circuit_font = FontFactory.regular(16)
        circuit_txt = text(circuit.name.upper(), (255,255,255), circuit_font)
        middle = (h-circuit_txt.height)//2
        paste(circuit_txt, img, flag_pos.right+10, top=middle-2)

        with Image.open(self.visual_config['bg_logo']) as logo:
            with Image.open(self.visual_config['bg_logo2']) as logo2:
                logo = resize(logo, height=int(2 * (h//3)))
                logo2 = resize(logo2, height=int(2 * (h//3)))
                paste(logo, img)
                paste(logo2, img, left=w-logo2.width)
        return img

    def _get_center_img(self, width:int, height: int) -> PngImageFile:
        # CIRCUIT
        with self.config.race.circuit.get_photo() as p:
            img = resize(p, height=height)
            crop_left = (img.width - width) // 2
            crop_top = (img.height - height) // 2
            img = img.crop((crop_left, crop_top, crop_left+width, crop_top+height))
        hsv = img.convert('HSV')
        h,s,v = hsv.split()
        h = h.point(lambda x:170)
        new = Image.merge('HSV', (h,s,v))
        return new.convert('RGB')

    def _get_driver_of_the_day_block_text_img(self, width:int, height:int) -> PngImageFile:
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        dotd_font = FontFactory.black(40)
        driver_text = text('DRIVER', (255,255,255), dotd_font)
        ofthe_text = text('OF THE', (255,255,255), dotd_font)
        day_text = text('DAY', (255,255,255), dotd_font)
        driver_pos = paste(driver_text, img, top=0, left=0)
        ofthe_pos = paste(ofthe_text, img, top=driver_pos.bottom, left=0)
        paste(day_text, img, top=ofthe_pos.bottom, left=0)
        return img