import logging, asyncio
from disnake.ext import commands
from f1_22_telemetry.packets import (
    Packet,
    PacketCarDamageData,
    PacketCarTelemetryData,
    PacketCarStatusData,
    PacketCarSetupData,
    PacketLapData,
    PacketSessionData,
    PacketSessionHistoryData,
    PacketMotionData,
    PacketParticipantsData,
    PacketEventData,
    PacketFinalClassificationData,
    PacketLobbyInfoData
)
from tabulate import tabulate

from src.telemetry.models.enums.driver_status import DriverStatus
from .managers.lap_record_manager import LapRecordManager
from datetime import datetime, timedelta

from src.telemetry.models.enums.safety_car_status import SafetyCarStatus
from .managers.classification_manager import ClassificationManager
from .managers.damage_manager import DamageManager
from .managers.lap_manager import LapManager
from .managers.participant_manager import ParticipantManager

from .managers.session_manager import SessionManager
from .managers.telemetry_manager import TelemetryManager

_logger = logging.getLogger(__name__)

DEFAULT_GUILD_ID = 1074380392154533958
DEFAULT_CHANNEL_ID = 1096169137589461082
WEATHER_NOTIFICATION_DELAY = 4 * 60 # 4 minutes

class Brain:
    def __init__(self, bot: commands.InteractionBot = None, discord_guild: str = DEFAULT_GUILD_ID, discord_channel: str = DEFAULT_CHANNEL_ID):
        self.current_session = None
        self.previous_sessions = []
        self.bot = bot
        self.last_weather_notified_at = None
        self.discord_guild = int(discord_guild) if discord_guild is not None else DEFAULT_GUILD_ID
        self.discord_channel = int(discord_channel) if discord_channel is not None else DEFAULT_CHANNEL_ID
        _logger.info(f'Will use {self.discord_guild}:{self.discord_channel} to send Discord messages')

    def handle_received_packet(self, packet: Packet):
        packet_type = type(packet)
        _logger.debug(f'Handling new {packet_type}')

        if packet_type == PacketSessionData:
            self._handle_received_session_packet(packet)

        elif packet_type == PacketParticipantsData:
            self._handle_received_participants_packet(packet)

        elif packet_type == PacketFinalClassificationData:
            self._handle_received_final_classification_packet(packet)

        elif packet_type == PacketCarDamageData:
            self._handle_received_damage_packet(packet)

        elif packet_type == PacketCarTelemetryData:
            self._handle_received_telemetry_packet(packet)

        elif packet_type == PacketLapData:
            self._handle_received_lap_packet(packet)

        elif packet_type == PacketSessionHistoryData:
            self._handle_received_session_history_packet(packet)

    def _send_discord_message(self, msg):
        if not self.bot:
            return
        if not self.bot.loop:
            return 
        if not self.discord_guild:
            return
        if not self.discord_channel:
            return

        _logger.info(f'Following msg ({len(msg)} chars) to be sent to Discord')
        _logger.info(msg)

        guild = self.bot.get_guild(self.discord_guild)
        if not guild:
            _logger.error(f'Guild "{self.discord_guild}" not found, message not sent')
            return

        channel = guild.get_channel(self.discord_channel)
        if not channel:
            _logger.error(f'Channel "{self.discord_channel}" not found, message not sent')
            return

        if channel.threads and len(channel.threads):
            where = channel.threads[-1]
        else:
            where = channel

        self.bot.loop.create_task(where.send(msg))

    def _handle_received_session_packet(self, packet: PacketSessionData):
        tmp_session = SessionManager.create(packet)
        if not self.current_session:
            _logger.info('A new session has started')
            self.current_session = tmp_session
            msg = f'Début de la session "{self.current_session.session_type}" à {self.current_session.track}'
            self._send_discord_message(msg)
            return

        if self.current_session == tmp_session:
            changes = SessionManager.update(self.current_session, packet)

            if 'weather_forecast' in changes:
                now = datetime.now()
                delta = now - self.last_weather_notified_at if self.last_weather_notified_at else None
                if not delta or delta.seconds > WEATHER_NOTIFICATION_DELAY:
                    wfcasts = self.current_session.weather_forecast
                    str_wfcasts = []
                    other_wfcasts = {}
                    for wfcast in wfcasts:
                        wf_values = str(wfcast)
                        if wfcast.session_type == self.current_session.session_type:
                            str_wfcasts.append(wf_values)
                        else:
                            other_wfcasts.setdefault(wfcast.session_type, [])
                            other_wfcasts[wfcast.session_type].append(wf_values)
                    for sess_type, wfcasts in other_wfcasts.items():
                        print('───────────────')
                        print(sess_type)
                        print('\n'.join(wfcasts))

                    msg = '\n'.join(str_wfcasts)
                    self._send_discord_message(msg)
                    self.last_weather_notified_at = now
            if 'safety_car_status' in changes:
                actual_status = changes['safety_car_status'].actual
                self._send_discord_message(str(actual_status))
        else:
            _logger.info('A new session has started, previous one has been backuped')
            self.previous_sessions.append(self.current_session)
            self.current_session = tmp_session
            msg = f'Début de la session "{self.current_session.session_type}" à {self.current_session.track}'
            self._send_discord_message(msg)

    def _handle_received_participants_packet(self, packet:PacketParticipantsData):
        if not self.current_session:
            return # we could store in a tmp self. variable and store info at session creation if needed
        if not self.current_session.participants:
            self.current_session.participants = [
                ParticipantManager.create(packet_data)
                for packet_data in packet.participants if packet_data.race_number != 0 # (0 means no participant)
            ]
        else:
            current_amount_of_participants = len(self.current_session.participants)
            for i, packet_data in enumerate(packet.participants):
                if packet_data.race_number != 0:
                    if i > current_amount_of_participants - 1:
                        self.current_session.participants.append(ParticipantManager.create(packet_data))
                    else:
                        changes = ParticipantManager.update(self.current_session.participants[i], packet_data)
                        if 'network_id' in changes or 'name' in changes:
                            _logger.warning('!? A participant changed !?')
                            _logger.warning(changes)

    def _handle_received_damage_packet(self, packet:PacketCarDamageData):
        if not self.current_session:
            return # this should not happen
        if not self.current_session.participants:
            return # this should not happen neither
        amount_of_pertinent_damages = len(self.current_session.participants)
        if not self.current_session.damages:
            self.current_session.damages = [
                DamageManager.create(packet.car_damage_data[i])
                for i in range(amount_of_pertinent_damages)
            ]
        else:
            current_amount_of_damage = len(self.current_session.damages)
            for i in range(amount_of_pertinent_damages):
                packet_data = packet.car_damage_data[i]
                if i > current_amount_of_damage - 1:
                    self.current_session.damages.append(DamageManager.create(packet_data))
                else:
                    changes = DamageManager.update(self.current_session.damages[i], packet_data)
                    participant = self.current_session.participants[i]
                    if DamageManager.has_noticeable_damage_changes(changes):
                        main_msg = f'**{participant}** → {DamageManager.get_changes_description(changes)}'
                        car_status = self.current_session.damages[i].get_current_status()
                        msg = '\n'.join([main_msg, car_status])
                        self._send_discord_message(msg)

    def _handle_received_telemetry_packet(self, packet:PacketCarTelemetryData):
        if not self.current_session:
            return # this should not happen
        if not self.current_session.participants:
            return # this should not happen neither
        amount_of_pertinent_telemetry = len(self.current_session.participants)
        if not self.current_session.telemetries:
            self.current_session.telemetries = [
                TelemetryManager.create(packet.car_telemetry_data[i])
                for i in range(amount_of_pertinent_telemetry)
            ]
        else:
            current_amount_of_telemetry = len(self.current_session.telemetries)
            for i in range(amount_of_pertinent_telemetry):
                packet_data = packet.car_telemetry_data[i]
                if i > current_amount_of_telemetry - 1:
                    self.current_session.telemetries.append(TelemetryManager.create(packet_data))
                else:
                    changes = TelemetryManager.update(self.current_session.telemetries[i], packet_data)
                    # if changes:
                        # pilot = self.current_session.participants[i].name
                        # _logger.info(f'{pilot} had a change in his telemetry !')
                        # _logger.info(changes)

    def _handle_received_final_classification_packet(self, packet:PacketFinalClassificationData):
        if not self.current_session:
            return # this should not happen
        if not self.current_session.final_classification:
            self.current_session.final_classification = [
                ClassificationManager.create(packet.classification_data[i])
                for i in range(packet.num_cars)
            ]
            self._send_discord_message(f'Fin de la session "{self.current_session.session_type}" voici le classement final :')
            for part in self._get_final_classification_as_string():
                self._send_discord_message(f"```\n{part}\n```")
        else:
            current_amount_of_classification = len(self.current_session.final_classification)
            at_least_one_changed = False
            for i in range(packet.num_cars):
                packet_data = packet.classification_data[i]
                if i > current_amount_of_classification - 1:
                    self.current_session.final_classification.append(ClassificationManager.create(packet_data))
                else:
                    changes = ClassificationManager.update(self.current_session.final_classification[i], packet_data)
                    if changes:
                        _logger.warning('!? final classification changed !?')
                        _logger.warning(changes)
                        at_least_one_changed = True
            if at_least_one_changed:
                self._send_discord_message('Le classement a changé !? Voici la nouvelle version:')
                for part in self._get_final_classification_as_string():
                    self._send_discord_message(f"```\n{part}\n```")

    def _handle_received_session_history_packet(self, packet: PacketSessionHistoryData):
        if not self.current_session:
            return # this should not happen
        if not self.current_session.participants:
            return # this should not happen neither
        if not self.current_session.lap_records:
            self.current_session.lap_records = [None] * 20
        if not self.current_session.lap_records[packet.car_idx]:
            self.current_session.lap_records[packet.car_idx] = LapRecordManager.create(packet)
        else:
            lap_record = self.current_session.lap_records[packet.car_idx]
            changes = LapRecordManager.update(lap_record, packet)
            amount_of_participants = len(self.current_session.participants)
            if packet.car_idx >= amount_of_participants:
                return

            driver = self.current_session.participants[packet.car_idx]
            if changes:
                if 'best_lap_time' in changes:
                    best_lap_time = changes["best_lap_time"].actual
                    lap_time = timedelta(seconds=best_lap_time/1000)
                    if not self.current_session.current_fastest_lap or best_lap_time < self.current_session.current_fastest_lap:
                        self.current_session.current_fastest_lap = best_lap_time
                        msg = f'🕒 🟪 **{driver}** : nouveau meilleur tour ! (`{self.current_session._format_time(lap_time)}`)'
                    else:
                        msg = f'🕒 🟩 **{driver}** : nouveau meilleur tour personnel ! (`{self.current_session._format_time(lap_time)}`)'
                    self._send_discord_message(msg)
                    return
                if not self.current_session.session_type.is_race():
                    keys = (
                        'best_sector1_time', 'best_sector2_time', 'best_sector3_time'
                    )
                    present_keys = list(filter(lambda x: x in changes, keys))
                    if present_keys:
                        txts = {
                            'best_sector1_time': 'Secteur 1',
                            'best_sector2_time': 'Secteur 2',
                            'best_sector3_time': 'Secteur 3'
                        }
                        session_mapping = {
                            'best_sector1_time': 'current_fastest_sector1',
                            'best_sector2_time': 'current_fastest_sector2',
                            'best_sector3_time': 'current_fastest_sector3'
                        }
                        for key in present_keys:
                            current_time = changes[key].actual
                            sector_time = timedelta(seconds=current_time/1000)

                            session_attr = session_mapping[key]
                            current_best = getattr(self.current_session, session_attr)
                            print(f'{driver} {key}: {sector_time} // PB = {changes[key].old} -- Overall Best : {current_best}')
                            if not current_best or current_time < current_best:
                                setattr(self.current_session, session_attr, current_time)
                                msg = f'🕒 🟪 **{driver}**: nouveau meilleur {txts[key]} ! (`{self.current_session._format_time(sector_time)}`)'
                            else:
                                msg = f'🕒 🟩 **{driver}**: nouveau meilleur {txts[key]} personnel ! (`{self.current_session._format_time(sector_time)}`)'

    def _get_final_classification_as_string(self):
        _logger.info('Final ranking of previous session below.')
        final_ranking = self.current_session.get_formatted_final_ranking()
        if self.current_session.session_type.is_race():
            colalign = ('right','left','right', 'left', 'right')
        else:
            colalign = ('right','left','right', 'right')
        if len(self.current_session.final_classification) > 15:
            return [
                tabulate(final_ranking[:10], tablefmt='simple_grid', colalign=colalign),
                tabulate(final_ranking[10:], tablefmt='simple_grid', colalign=colalign)
            ]
        return [tabulate(final_ranking, tablefmt='simple_grid', colalign=colalign)]

    def _handle_received_lap_packet(self, packet:PacketLapData):
        if not self.current_session:
            return # this should not happen
        if not self.current_session.participants:
            return # this should not happen neither

        amount_of_pertinent_lap = len(self.current_session.participants)
        # NO LAPS yet, create for all participants
        if not self.current_session.laps:
            self.current_session.laps = []
            self.current_session.lap_state_last_start_of_lap = []
            for i in range(amount_of_pertinent_lap):
                self.current_session.laps.append([
                    LapManager.create(packet.lap_data[i], 0)
                ])
                self.current_session.lap_state_last_start_of_lap.append(
                    LapManager.create(packet.lap_data[i], 0)
                )
        else:
            current_amount_of_lap = len(self.current_session.laps)
            for i in range(amount_of_pertinent_lap):
                packet_data = packet.lap_data[i]

                # We had no laps yet for this one
                if i > current_amount_of_lap - 1:
                    self.current_session.laps.append([])
                    self.current_session.lap_state_last_start_of_lap.append(None)

                car_laps = self.current_session.laps[i]
                car_last_lap = car_laps[-1] if car_laps else None
                pilot = self.current_session.participants[i]

                # pilot lap records (best sectors & lap)
                if self.current_session.lap_records:
                    all_lap_records = self.current_session.lap_records
                else:
                    all_lap_records = None
                lap_records = all_lap_records[i] if all_lap_records and i < len(all_lap_records) else None

                # Same lap
                if car_last_lap and car_last_lap.current_lap_num == packet_data.current_lap_num:
                    changes = LapManager.update(car_last_lap, packet_data)

                    if 'result_status' in changes:
                        result_status = changes['result_status'].actual
                        msg = result_status.get_pilot_result_str(pilot)
                        if msg:
                            self._send_discord_message(msg)
                    # DON'T DO THE FOLLOWING IN RACE
                    if not self.current_session.session_type.is_race() and car_last_lap.driver_status not in (DriverStatus.in_pit, DriverStatus.out_lap):
                        if 'current_lap_invalid' in changes and car_last_lap.current_lap_invalid:
                            square_repr = '🟥🟥🟥'
                            msg = f'**{pilot}** : {square_repr}'
                            self._send_discord_message(msg)
                        if lap_records and ('sector1_time_in_ms' in changes or 'sector2_time_in_ms' in changes) and not car_last_lap.current_lap_invalid:
                            pb_sector1 = lap_records.best_sector1_time
                            ob_sector1 = self.current_session.current_fastest_sector1

                            pb_sector2 = lap_records.best_sector2_time
                            ob_sector2 = self.current_session.current_fastest_sector2

                            square_repr = car_last_lap.get_squared_repr(pb_sector1, ob_sector1, pb_sector2, ob_sector2, None, None, None)

                            msg = f'**{pilot}** : {square_repr}'
                            self._send_discord_message(msg)

                # Pilot just crossed the line
                else:
                    # Add the new lap to the car's list of lap
                    new_lap = LapManager.create(packet_data, len(car_laps))
                    car_laps.append(new_lap)

                    # -- RACE
                    if self.current_session.session_type.is_race():
                        # If it's the lap of the race leader, notify new lap
                        if new_lap.car_position == 1:
                            msg = (
                                '━━━━━━━━━━━━━━'
                                f'{new_lap.get_lap_num_title(self.current_session.total_laps)}'
                                '━━━━━━━━━━━━━━'
                            )
                            self._send_discord_message(msg)
                    # -- QUALIFS
                    else:
                        if lap_records and not car_last_lap.current_lap_invalid and car_last_lap.driver_status not in (DriverStatus.in_pit, DriverStatus.out_lap):
                            pb_sector1 = lap_records.best_sector1_time
                            ob_sector1 = self.current_session.current_fastest_sector1

                            pb_sector2 = lap_records.best_sector2_time
                            ob_sector2 = self.current_session.current_fastest_sector2

                            pb_sector3 = lap_records.best_sector3_time
                            ob_sector3 = self.current_session.current_fastest_sector3

                            square_repr = car_last_lap.get_squared_repr(pb_sector1, ob_sector1, pb_sector2, ob_sector2, new_lap.last_lap_time_in_ms, pb_sector3, ob_sector3)

                            msg = f'**{pilot}** : {square_repr}'
                            self._send_discord_message(msg)

                    # Compare with lap state last time pilot crossed the line...
                    old_lap_state = self.current_session.lap_state_last_start_of_lap[i]

                    # Notify position change if any
                    if old_lap_state and old_lap_state.car_position != new_lap.car_position:
                        position_change = new_lap.get_position_evolution(old_lap_state)
                        if position_change:
                            msg = f'{position_change} **{pilot}**'
                        self._send_discord_message(msg)

                    # .. and update it
                    self.current_session.lap_state_last_start_of_lap[i] = LapManager.create(packet_data, len(car_laps))