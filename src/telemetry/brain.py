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

from src.telemetry.models.enums.safety_car_status import SafetyCarStatus
from .managers.classification_manager import ClassificationManager
from .managers.damage_manager import DamageManager
from .managers.lap_manager import LapManager
from .managers.participant_manager import ParticipantManager

from .managers.session_manager import SessionManager
from .managers.telemetry_manager import TelemetryManager

_logger = logging.getLogger(__name__)

DAMAGE_GUILD_ID = 1074380392154533958
DAMAGE_CHANNEL_ID = 1074380392720773312

class Brain:
    def __init__(self, bot:commands.InteractionBot=None):
        self.current_session = None
        self.previous_sessions = []
        self.bot = bot

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
        if self.bot and self.bot.loop:
            self.bot.loop.create_task(
                self.bot.get_guild(DAMAGE_GUILD_ID).get_channel(DAMAGE_CHANNEL_ID).send(msg)
            )

    def _handle_received_session_packet(self, packet: PacketSessionData):
        tmp_session = SessionManager.create(packet)
        if not self.current_session:
            _logger.info('A new session has started')
            self.current_session = tmp_session
            return

        if self.current_session == tmp_session:
            changes = SessionManager.update(self.current_session, packet)
            if 'weather_forecast' in changes:
                print('Forecast has changed !')
                print(self.current_session.weather_forecast)
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

    def _handle_received_participants_packet(self, packet:PacketParticipantsData):
        if not self.current_session:
            return # we could store in a tmp self. variable and store info at session creation if needed
        if not self.current_session.participants:
            self.current_session.participants = [
                ParticipantManager.create(packet.participants[i])
                for i in range(packet.num_active_cars)
            ]
        else:
            current_amount_of_participants = len(self.current_session.participants)
            for i in range(packet.num_active_cars):
                packet_data = packet.participants[i]
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
                    if changes and any(key in changes for key in damage_keys.keys()):
                        changed_parts = []
                        status_parts = []
                        for key in damage_keys.keys():
                            if key in changes:
                                changed_parts.append(damage_keys[key].strip())
                            damage_value = getattr(damages, key)
                            damage_value_str = self._padded_percent(damage_value)
                            status_parts.append(f'{damage_keys[key]}: {damage_value_str} {self._get_status_bar(damage_value)}')

                        msg_parts = [
                            f'**{participant.name}** a subi/réparé des dégats concernant : {", ".join(changed_parts)}',
                            '```',
                            '\n'.join(status_parts),
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
        else:
            current_amount_of_classification = len(self.current_session.final_classification)
            for i in range(packet.num_cars):
                packet_data = packet.classification_data[i]
                if i > current_amount_of_classification - 1:
                    self.current_session.final_classification.append(ClassificationManager.create(packet_data))
                else:
                    changes = ClassificationManager.update(self.current_session.final_classification[i], packet_data)
                    if changes:
                        _logger.warning('!? final classification changed !?')
                        _logger.warning(changes)

    def _handle_received_lap_packet(self, packet:PacketLapData):
        if not self.current_session:
            return # this should not happen
        if not self.current_session.participants:
            return # this should not happen neither
        amount_of_pertinent_lap = len(self.current_session.participants)
        if not self.current_session.laps:
            self.current_session.laps = [
                [LapManager.create(packet.lap_data[i], 0)]
                for i in range(amount_of_pertinent_lap)
            ]
        else:
            current_amount_of_lap = len(self.current_session.laps)
            for i in range(amount_of_pertinent_lap):
                packet_data = packet.lap_data[i]
                if i > current_amount_of_lap - 1:
                    self.current_session.laps.append([])

                car_laps = self.current_session.laps[i]
                car_last_lap = car_laps[-1] if car_laps else None
                if not car_last_lap or car_last_lap.current_lap_num != packet_data.current_lap_num:
                    car_laps.append(LapManager.create(packet_data, len(car_laps)))
                else:
                    changes = LapManager.update(car_last_lap, packet_data)

                    if 'car_position' in changes:
                        change = changes['car_position']
                        pilot = self.current_session.participants[i].name
                        delta = change.actual - change.old
                        if delta == 1:
                            _logger.warning(f'{pilot} lost a position ({change.old} -> {change.actual}) !')
                        elif delta > 1:
                            _logger.warning(f'{pilot} lost {delta} positions ({change.old} -> {change.actual}) !')
                        elif delta == -1:
                            _logger.warning(f'{pilot} gained a position ({change.old} -> {change.actual}) !')
                        elif delta < -1:
                            _logger.warning(f'{pilot} gained {-delta} positions ({change.old} -> {change.actual}) !')

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
