from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngImageFile
from src.media_generation.font_factory import FontFactory
from src.media_generation.helpers.transform import line, paste, resize, text, text_hi_res
from src.media_generation.data import RESERVIST_TEAM, teams_idx
from src.media_generation.models.pilot import Pilot
from src.telemetry.models.car_status import CarStatus
from src.telemetry.models.damage import Damage
from src.telemetry.models.enums.team import Team
from src.telemetry.models.enums.tyre import Tyre
from src.telemetry.models.lap import Lap
from src.telemetry.models.lap_record import LapRecord
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session

IMPROVEMENT_COLOR = (85, 225, 80)
FASTEST_COLOR = (145, 75, 155)
SLOWER_COLOR = (250, 220, 0)
EMPTY_COLOR = (126, 126, 126)

class TimeBoxGenerator:

    def generate(self, lap: Lap, lap_record: LapRecord, participant: Participant, car_status: CarStatus, session: Session):
        out = Image.new('RGB', (400, 135), (0, 0, 0))
        pilot_height = 45
        pilot_img = self._get_pilot_image(out.width, pilot_height, lap.car_position, participant, car_status)
        pilot_position = paste(pilot_img, out, left=0, top=0)

        sectors_imgs = self._get_sectors_image(out.width, out.height - pilot_height, lap, lap_record, session)
        paste(sectors_imgs, out, left=0, top=pilot_position.bottom)

        path = f'output/timeboxes/{participant.name.lower()}.png'
        out.save(path, quality=95)
        return path

    def _get_pilot_image(self, width: int, height: int, position: int, participant: Participant, car_status: CarStatus):
        team = teams_idx.get(str(participant.team), RESERVIST_TEAM)
        pilot = Pilot(participant.name, team, participant.race_number)
        team_width = 50
        pilot_width = width - 45 - team_width - 45
        #  45px  45px                    45px
        # [POS] [LOGO] [NAME]           [TYRE]
        out = Image.new('RGB', (width, height), (210, 210, 210))
        position_position = paste(self._get_pilot_position_image(45, height, position), out, left=0)
        team_position = paste(self._get_pilot_team_image(team_width, height, pilot), out, left=position_position.right)
        pilot_position = paste(self._get_pilot_name_image(pilot_width, height, pilot), out, left=team_position.right)
        paste(self._get_pilot_tyre_image(
            45, height, car_status.visual_tyre_compound), out, left=pilot_position.right)
        return out

    def _get_sectors_image(self, width: int, height: int, lap:Lap, lap_record:LapRecord, session: Session):
        img = Image.new('RGB', (width, height), (0,0,0))
        sector_width = width // 3
        last_sector_width = width - 2 * sector_width
        current_s1 = lap.sector_1_time_in_ms
        current_s2 = lap.sector_2_time_in_ms
        current_s3 = lap.sector_3_time_in_ms
        personal_best_s1 =  lap_record.best_sector1_time
        personal_best_s2 =  lap_record.best_sector2_time
        personal_best_s3 =  lap_record.best_sector3_time
        personal_best_lap = lap_record.best_lap_time
        overal_best_s1 = session.current_fastest_sector1
        overal_best_s2 = session.current_fastest_sector2
        overal_best_s3 = session.current_fastest_sector3
        overal_fastest_lap = session.current_fastest_lap

        current_lap_time = current_s1
        personal_best_ongoing = personal_best_s1
        overal_best_ongoing = overal_best_s1
        s1_img = self._get_sector_image(1, sector_width, height, current_s1, personal_best_s1, overal_best_s1, current_lap_time, personal_best_ongoing, overal_best_ongoing)
        s1_position = paste(s1_img, img, left=0)

        current_lap_time = (current_lap_time + current_s2) if current_lap_time and current_s2 else current_lap_time
        personal_best_ongoing = (personal_best_ongoing + personal_best_s2) if personal_best_ongoing and personal_best_s2 else personal_best_lap
        overal_best_ongoing = (overal_best_ongoing + overal_best_s2) if overal_best_ongoing and overal_best_s2 else personal_best_lap
        s2_img = self._get_sector_image(2, sector_width, height, current_s2, personal_best_s2, overal_best_s2, current_lap_time, personal_best_ongoing, overal_best_ongoing)
        s2_position = paste(s2_img, img, left=s1_position.right)

        current_lap_time = (current_lap_time + current_s3) if current_lap_time and current_s3 else current_lap_time
        personal_best_ongoing = personal_best_lap
        overal_best_ongoing = overal_fastest_lap

        s3_img = self._get_sector_image(3, last_sector_width, height, current_s3, personal_best_s3, overal_best_s3, current_lap_time, personal_best_ongoing, overal_best_ongoing)
        paste(s3_img, img, left=s2_position.right)
        return img

    def _get_pilot_position_image(self, width: int, height: int, position: int):
        out = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        color = (0, 0, 0)
        font = FontFactory.bold(6)
        padding = 10
        txt = text_hi_res(position, color, font, (width-padding), (height-padding))
        paste(txt, out)
        return out

    def _get_pilot_team_image(self, width: int, height: int, pilot: Pilot):
        bg_color = pilot.team.standing_bg
        out = Image.new('RGBA', (width, height), bg_color)
        padding = 10
        use_white_logo = ['McLaren', 'AlfaRomeo']
        logo_fct = Image.open(pilot.team._get_white_logo_path(
        )) if pilot.team.name in use_white_logo else pilot.team.get_results_logo()
        with logo_fct as logo:
            logo = resize(logo, width-padding, height-padding)
            paste(logo, out)

        return out

    def _get_pilot_name_image(self, width: int, height: int, pilot: Pilot):
        out = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        color = (0, 0, 0)
        font = FontFactory.bold(6)
        padding = 10
        txt = text_hi_res(pilot.name.upper(), color, font, width-padding, height-padding)
        paste(txt, out, left=10)
        return out

    def _get_pilot_tyre_image(self, width: int, height: int, tyre: Tyre):
        out = Image.new('RGB', (width, height), (0, 0, 0))
        padding = 15
        with Image.open(f'./assets/tyres/{str(tyre)}.png') as tyre_img:
            paste(resize(tyre_img, width-padding, height-padding), out, left=8)
        return out

    def _get_sector_image(self, sector:int, width: int, height: int, current:int, personal_best:int, overall_best:int, current_lap_time:int, personal_best_ongoing_lap_time:int, overall_best_ongoing_lap_time):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        bottom_height = 30
        if not current:
            bottom_color = EMPTY_COLOR
        elif not overall_best or current < overall_best:
            bottom_color = FASTEST_COLOR
        elif not personal_best or current < personal_best:
            bottom_color = IMPROVEMENT_COLOR
        else:
            bottom_color = SLOWER_COLOR

        if not current_lap_time:
            top_color = EMPTY_COLOR
        elif not overall_best_ongoing_lap_time or current_lap_time < overall_best_ongoing_lap_time:
            top_color = IMPROVEMENT_COLOR
        else:
            top_color = SLOWER_COLOR

        # BOTTOM IMG
        bottom_img = self._get_sector_bottom_image(sector, width, bottom_height, bottom_color, current)
        paste(bottom_img, img, left=0, top=height-bottom_height)

        if not current:
            return img

        # TOP IMG
        delta = current_lap_time - overall_best_ongoing_lap_time if overall_best_ongoing_lap_time else None
        top_img = self._get_sector_top_image(width, height-bottom_height, top_color, current_lap_time, delta)
        paste(top_img, img, left=0, top=0)
        return img


    def _get_sector_top_image(self, width:int, height:int, color:tuple, current_lap_time: int, delta_to_fastest:int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        if not current_lap_time:
            return img

        font = FontFactory.bold(6)
        f_current = self._format_time(current_lap_time)
        top = 5 if delta_to_fastest else 15
        time_height = int(0.25 * height) if delta_to_fastest is not None else int(height)
        current_img = text_hi_res(f_current, (255,255,255), font, width, time_height)
        paste(current_img, img, top=top)

        if delta_to_fastest:
            delta_font = FontFactory.regular(6)
            delta_operator = '-' if delta_to_fastest < 0 else '+'
            delta_height = height - time_height
            f_delta = f'{delta_operator}{self._format_time(delta_to_fastest)}'
            delta_img = text_hi_res(f_delta, color, delta_font, width, delta_height)
            paste(delta_img, img, top=height-delta_img.height - 10)

        return img

    def _get_sector_bottom_image(self, sector:int, width:int, height:int, color:tuple, current: int):
        img = Image.new('RGBA', (width, height), (0,0,0,0))
        font = FontFactory.regular(6)

        line_height = 3
        padding_bottom = 2
        line = Image.new('RGB', (width, line_height), color)
        paste(line, img, left=0, top=height-(line_height + padding_bottom))

        remaining_height = height - line.height
        text_padding = 10
        if current:
            formatted_sector_time = self._format_time(current)
        else:
            formatted_sector_time = f'S{sector}'
        sector_time = text_hi_res(formatted_sector_time, color, font, width-text_padding, remaining_height-text_padding)
        paste(sector_time, img, top=0)

        return img

    def _format_time(self, milliseconds:int):
        milliseconds = abs(milliseconds)
        if milliseconds == 0:
            return '0.000'

        full_seconds = milliseconds // 1000
        minutes = full_seconds // 60
        minutes_str = f'{minutes}:' if minutes > 0 else ''

        seconds = full_seconds % 60
        seconds_str = str(seconds).zfill(2) if minutes > 0 else seconds

        milliseconds = milliseconds % 1000
        milliseconds_str = str(milliseconds).zfill(3)

        return f'{minutes_str}{seconds_str}.{milliseconds_str}'
