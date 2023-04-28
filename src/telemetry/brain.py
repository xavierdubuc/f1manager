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
from src.telemetry.models.enums.result_status import ResultStatus
from datetime import datetime

from src.telemetry.models.enums.safety_car_status import SafetyCarStatus
from .managers.classification_manager import ClassificationManager
from .managers.damage_manager import DamageManager
from .managers.lap_manager import LapManager
from .managers.participant_manager import ParticipantManager

from .managers.session_manager import SessionManager
from .managers.telemetry_manager import TelemetryManager

_logger = logging.getLogger(__name__)

DAMAGE_GUILD_ID = 1074380392154533958
DAMAGE_CHANNEL_ID = 1096169137589461082

class Brain:
    def __init__(self, bot:commands.InteractionBot=None):
        self.current_session = None
        self.previous_sessions = []
        self.bot = bot
        self.last_weather_notified_at = None

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

    def _send_discord_message(self, msg):
        _logger.info('Following msg to be sent to Discord')
        _logger.info(msg)
        _logger.info(f'{len(msg)} chars')
        if self.bot and self.bot.loop:
            guild = self.bot.get_guild(DAMAGE_GUILD_ID)
            if guild:
                channel = guild.get_channel(DAMAGE_CHANNEL_ID)
                if channel:
                    self.bot.loop.create_task(channel.send(msg))

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
                if not delta or delta.seconds > 5 * 60:
                    wfcasts = self.current_session.weather_forecast
                    rows = []
                    for wfcast in wfcasts:
                        if wfcast.session_type == self.current_session.session_type:
                            rows.append([
                                f'+{wfcast.time_offset}min',
                                str(wfcast.weather),
                                f'{wfcast.rain_percentage}% pluie',
                                f'Circuit: {wfcast.track_temperature}°C',
                                f'Air: {wfcast.air_temperature}°C',
                            ])
                    msg = tabulate(rows, tablefmt='simple_grid')
                    self._send_discord_message(f"```\n{msg}\n```")
                    self.last_weather_notified_at = now
            if 'safety_car_status' in changes:
                actual_status = changes['safety_car_status'].actual
                if actual_status == SafetyCarStatus.virtual:
                    msg = '⚠️ 🟡 VIRTUAL SAFETY CAR 🟡 ⚠️'
                elif actual_status == SafetyCarStatus.full:
                    msg = '⛔ 🔴 FULL SAFETY CAR 🔴 ⛔'
                elif actual_status == SafetyCarStatus.no:
                    msg = '🟢 DRAPEAU VERT 🟢'
                self._send_discord_message(msg)
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
                    participant = self.current_session.participants[i]
                    damage_keys = {
                        'front_left_wing_damage':  'Aileron avant gauche',
                        'front_right_wing_damage': ' Aileron avant droit',
                        'rear_wing_damage':        '     Aileron arrière',
                        'floor_damage':            '           Fond plat',
                        'diffuser_damage':         '           Diffuseur',
                        'sidepod_damage':          '            Sidepods',
                    }
                    changes = DamageManager.update(self.current_session.damages[i], packet_data)
                    damages = self.current_session.damages[i]
                    has_damage_changes = any(key in changes for key in damage_keys.keys()) or 100 in damages.tyres_damage
                    is_increase = True
                    is_decrease = False
                    if changes and has_damage_changes:
                        changed_parts = []
                        status_parts = []
                        if damages.tyres_damage[0] == 100:
                            changed_parts.append('Crevaison/Roue arrière gauche arrachée')
                        if damages.tyres_damage[1] == 100:
                            changed_parts.append('Crevaison/Roue arrière droite arrachée')
                        if damages.tyres_damage[2] == 100:
                            changed_parts.append('Crevaison/Roue avant gauche arrachée')
                        if damages.tyres_damage[3] == 100:
                            changed_parts.append('Crevaison/Roue avant droite arrachée')
                        for key in damage_keys.keys():
                            if key in changes:
                                changed_parts.append(damage_keys[key].strip())
                                if changes[key].old < changes[key].actual:
                                    is_increase = True
                                else:
                                    is_decrease = True
                            damage_value = getattr(damages, key)
                            damage_value_str = self._padded_percent(damage_value)
                            status_parts.append(f'{damage_keys[key]}: {damage_value_str} {self._get_status_bar(damage_value)}')

                        verb = (
                            f"{'a subi' if is_increase else ''}"
                            "/" if is_increase and is_decrease else ''
                            f"{'a réparé' if is_decrease else ''}"
                        )
                        msg_parts = [
                            f'**{participant}** {verb} des dégats concernant : {", ".join(changed_parts)}',
                            '```',
                            '\n'.join(status_parts),
                            f'[{str(damages.tyres_damage[2]).rjust(3)}% ] --- [{str(damages.tyres_damage[3]).rjust(3)}% ]',
                            f'         |         ',
                            f'[{str(damages.tyres_damage[0]).rjust(3)}% ] --- [{str(damages.tyres_damage[1]).rjust(3)}% ]',
                            '```',
                        ]
                        msg = '\n'.join(msg_parts)
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
            self._send_discord_message("Fin de la session voici le classement final :")
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

                # Same lap
                if car_last_lap and car_last_lap.current_lap_num == packet_data.current_lap_num:
                    changes = LapManager.update(car_last_lap, packet_data)

                    if 'result_status' in changes:
                        result_status = changes['result_status'].actual
                        msg = result_status.get_pilot_result_str(pilot)
                        if msg:
                            self._send_discord_message(msg)
                # Pilot just crossed the line
                else:
                    # Add the new lap to the car's list of lap
                    new_lap = LapManager.create(packet_data, len(car_laps))
                    car_laps.append(new_lap)

                    # If it's the lap of the race leader and session is a race
                    # then notify new lap
                    if self.current_session.session_type.is_race() and car_laps[-1].car_position == 1:
                        msg = (
                            '━━━━━━━━━━━━━━'
                            f'{new_lap.get_lap_num_title()}'
                            '━━━━━━━━━━━━━━'
                        )
                        self._send_discord_message(msg)

                    # Compare with lap state last time pilot crossed the line...
                    old_lap_state = self.current_session.lap_state_last_start_of_lap[i]

                    # Notify position change if any
                    if old_lap_state and old_lap_state.car_position != new_lap.car_position:
                        position_change = new_lap.get_position_evolution(old_lap_state)
                        if position_change:
                            msg = f'**{pilot}** {position_change}'
                        self._send_discord_message(msg)

                    # .. and update it
                    self.current_session.lap_state_last_start_of_lap[i] = LapManager.create(packet_data, len(car_laps))

    def _padded_percent(self, percent):
        if 100 > percent > 9:
            return f' {percent}%'
        if percent <= 9:
            return f'  {percent}%'
        return f'{percent}%'

    def _get_status_bar(self, value, max_value=100):
        percent = 100 * (value/max_value)
        amount_of_char = int(percent // 10) # (ex 87% --> 8 chars)
        return f'[{"="*amount_of_char}{" "*(10-amount_of_char)}]'
