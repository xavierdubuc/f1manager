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

from src.telemetry.models.enums.safety_car_status import SafetyCarStatus
from .managers.classification_manager import ClassificationManager
from .managers.damage_manager import DamageManager
from .managers.lap_manager import LapManager
from .managers.participant_manager import ParticipantManager

from .managers.session_manager import SessionManager
from .managers.telemetry_manager import TelemetryManager

_logger = logging.getLogger(__name__)

DAMAGE_GUILD_ID = 923505034778509342
DAMAGE_CHANNEL_ID = 1098673162310397982

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
        _logger.info(f'{len(msg)} chars')
        if self.bot and self.bot.loop:
            self.bot.loop.create_task(
                self.bot.get_guild(DAMAGE_GUILD_ID).get_channel(DAMAGE_CHANNEL_ID).send(msg)
            )

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
                wfcasts = self.current_session.weather_forecast
                rows = []
                for wfcast in wfcasts:
                    rows += [
                        f'+{wfcast.time_offset}min',
                        str(wfcast.weather),
                        f'{wfcast.rain_percentage}% pluie',
                        f'Circuit: {wfcast.track_temperature}°C',
                        f'Air: {wfcast.air_temperature}°C',
                    ]
                msg = tabulate(rows, tablefmt='simple_grid'),
                self._send_discord_message(msg)
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
                    has_damage_changes = any(key in changes for key in damage_keys.keys()) or 100 in damages.tyres_damage
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
                            damage_value = getattr(damages, key)
                            damage_value_str = self._padded_percent(damage_value)
                            status_parts.append(f'{damage_keys[key]}: {damage_value_str} {self._get_status_bar(damage_value)}')

                        msg_parts = [
                            f'**{participant.name}** a subi/réparé des dégats concernant : {", ".join(changed_parts)}',
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
                    if self.current_session.session_type.is_race() and car_laps[-1].car_position == 1:
                        self._send_discord_message(f'--- Tour {car_laps[-1].current_lap_num} ---')
                else:
                    pilot = self.current_session.participants[i].name
                    changes = LapManager.update(car_last_lap, packet_data)

                    # TODO essayer d'inclure une notion de durée pour éviter d'avoir 45 changements quand y'a une bataille
                    # Ex : afficher le premier puis attendre 10 secondes, si a rechangé on remet un message
                    # Ne pas envoyer les messages si le gars pit, on envoit un message à la fin du pit avec le nombre
                    # total de position perdue par ex ? (moyen de stocker sur le lap précédent à priori ou sur le pilot directement)
                    if 'car_position' in changes:
                        change = changes['car_position']
                        delta = change.actual - change.old
                        actual_str = f' P{change.actual}' if change.actual < 10 else f'P{change.actual}'
                        if delta >= 1:
                            msg = f'`{actual_str}` (🔻 {delta}) **{pilot}**'
                        else:
                            msg = f'`{actual_str}` (🔼 {-delta}) **{pilot}**'
                        print(msg)
                        # self._send_discord_message(msg)

                    if 'result_status' in changes:
                        if changes['result_status'].actual == ResultStatus.finished:
                            msg = f'🏁 **{pilot}**'
                            self._send_discord_message(msg)
                        if changes['result_status'].actual == ResultStatus.dnf:
                            msg = f'🟥 **{pilot}** a NT'
                            self._send_discord_message(msg)
                        if changes['result_status'].actual == ResultStatus.dsq:
                            msg = f'🟥 **{pilot}** a été disqualifié'
                            self._send_discord_message(msg)
                        if changes['result_status'].actual == ResultStatus.retired:
                            msg = f'🟥 **{pilot}** a abandonné'
                            self._send_discord_message(msg)

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
