import logging
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
from src.telemetry.event import Event
from src.telemetry.listeners.classification_listener import ClassificationListener
from src.telemetry.listeners.noticeable_damage_listener import NoticeableDamageListener
from src.telemetry.listeners.safety_car_listener import SafetyCarListener
from src.telemetry.listeners.session_creation_listener import SessionCreationListener
from src.telemetry.listeners.weather_forecast_listener import WeatherForecastListener
from src.telemetry.message import Channel, Message

from src.telemetry.models.enums.driver_status import DriverStatus
from src.telemetry.models.enums.session_type import SessionType
from .managers.lap_record_manager import LapRecordManager
from datetime import timedelta

from .managers.classification_manager import ClassificationManager
from .managers.damage_manager import DamageManager
from .managers.lap_manager import LapManager
from .managers.participant_manager import ParticipantManager
from .managers.session_manager import SessionManager
from .managers.telemetry_manager import TelemetryManager

_logger = logging.getLogger(__name__)

LISTENER_CLASSES = [
    ClassificationListener,
    NoticeableDamageListener,
    SessionCreationListener,
    SafetyCarListener,
    WeatherForecastListener,
]

DEFAULT_GUILD_ID = 1074380392154533958
DEFAULT_CHANNEL_ID = 1096169137589461082

class Brain:
    def __init__(self, bot: commands.InteractionBot = None, championship_config:dict=None):
        self.current_session = None
        self.previous_sessions = []
        self.bot = bot
        self.last_weather_notified_at = None
        self.championship_config = championship_config
        self.listeners_by_event = {event: [] for event in Event}
        for Listener in LISTENER_CLASSES:
            listener = Listener()
            for event in Listener.SUBSCRIBED_EVENTS:
                self.listeners_by_event[event].append(listener)

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

    def _send_discord_message(self, msg:Message, parent_msg:Message=None):
        if not self.bot:
            return
        if not self.bot.loop:
            return
        if msg.channel == Channel.BROADCAST:
            channels = [c for c in Channel if c != Channel.BROADCAST]
            for channel in channels:
                self._send_discord_message(Message(content=msg.content, channel=channel), parent_msg=msg)
                return

        _logger.info(f'Following msg ({len(msg)} chars) to be sent to Discord ({msg.channel})')
        _logger.info(msg.content)

        discord_config = self.championship_config['discord'].get(msg.channel)
        if not discord_config:
            if parent_msg:
                _logger.debug(f'Message will not be broadcasted on channel {msg.channel} as no specific config for it')
                return

            _logger.info(f'No discord config for {msg.channel}, will use default')
            discord_config = self.championship_config['discord']['default']

        guild = self.bot.get_guild(discord_config['guild'])
        if not guild:
            _logger.error(f'Guild "{discord_config["guild"]}" not found, message not sent')
            return

        channel = guild.get_channel(discord_config['chann'])
        if not channel:
            _logger.error(f'Channel "{discord_config["chann"]}" not found, message not sent')
            return

        where = channel
        if discord_config.get('use_thread', False) and channel.threads and len(channel.threads):
            where = channel.threads[-1]

        _logger.info(f'Message sent to "{guild.name}/#{channel.name}')
        self.bot.loop.create_task(where.send(msg.get_content()))

    def _emit(self, event:Event, *args, **kwargs):
        _logger.debug(f'{event.name} emitted !')
        for listener in self.listeners_by_event[event]:
            msgs = listener.on(event, *args, **kwargs)
            if msgs:
                for msg in msgs:
                    self._send_discord_message(msg)

    """
    @emits SESSION_CREATED
    @emits SESSION_UPDATED
    """
    def _handle_received_session_packet(self, packet: PacketSessionData):
        tmp_session = SessionManager.create(packet)

        if self.current_session == tmp_session:
            changes = SessionManager.update(self.current_session, packet)
            self._emit(Event.SESSION_UPDATED, session=self.current_session, changes=changes)
        else:
            self._emit(Event.SESSION_CREATED, current=tmp_session, old=self.current_session)
            if not self.current_session:
                self.current_session = tmp_session
            else:
                _logger.info('A new session has started, previous one has been backuped')
                self.previous_sessions.append(self.current_session)
                self.current_session = tmp_session

    """
    @emits PARTICIPANT_CREATED
    @emits PARTICIPANT_LIST_INITIALIZED
    @emits PARTICIPANT_UPDATED
    """
    def _handle_received_participants_packet(self, packet:PacketParticipantsData):
        if not self.current_session:
            return # we could store in a tmp self. variable and store info at session creation if needed
        if not self.current_session.participants:
            self.current_session.participants = [
                ParticipantManager.create(packet_data)
                for packet_data in packet.participants if packet_data.race_number != 0 # (0 means no participant)
            ]
            self._emit(Event.PARTICIPANT_LIST_INITIALIZED, session=self.current_session, participants=self.current_session.participants)
        else:
            current_amount_of_participants = len(self.current_session.participants)
            for i, packet_data in enumerate(packet.participants):
                if packet_data.race_number != 0:
                    if i > current_amount_of_participants - 1:
                        new_participant = ParticipantManager.create(packet_data)
                        self._emit(Event.PARTICIPANT_CREATED, session=self.current_session, participant=new_participant)
                        self.current_session.participants.append(new_participant)
                    else:
                        changes = ParticipantManager.update(self.current_session.participants[i], packet_data)
                        self._emit(Event.PARTICIPANT_UPDATED, self.current_session.participants[i], changes, self.current_session)
                        if 'network_id' in changes or 'name' in changes:
                            _logger.warning('!? A participant changed !?')
                            _logger.warning(changes)

    """
    @emits DAMAGE_CREATED
    @emits DAMAGE_LIST_INITIALIZED
    @emits DAMAGE_UPDATED
    """
    def _handle_received_damage_packet(self, packet:PacketCarDamageData):
        if not self.current_session:
            return # this should not happen
        if not self.current_session.participants:
            return # this should not happen neither
        if self.current_session.session_type == SessionType.clm:
            return # this has no sense
        amount_of_pertinent_damages = len(self.current_session.participants)
        if not self.current_session.damages:
            self.current_session.damages = [
                DamageManager.create(packet.car_damage_data[i])
                for i in range(amount_of_pertinent_damages)
            ]
            self._emit(Event.DAMAGE_LIST_INITIALIZED, session=self.current_session, damages=self.current_session.damages)
        else:
            current_amount_of_damage = len(self.current_session.damages)
            for i in range(amount_of_pertinent_damages):
                packet_data = packet.car_damage_data[i]
                if i > current_amount_of_damage - 1:
                    new_damage = DamageManager.create(packet_data)
                    self.current_session.damages.append(new_damage)
                    self._emit(Event.DAMAGE_CREATED, session=self.current_session, damage=new_damage)
                else:
                    changes = DamageManager.update(self.current_session.damages[i], packet_data)
                    participant = self.current_session.participants[i]
                    self._emit(Event.DAMAGE_UPDATED, self.current_session.damages[i], changes, participant, self.current_session)

    """
    @emits TELEMETRY_CREATED
    @emits TELEMETRY_LIST_INITIALIZED
    @emits TELEMETRY_UPDATED
    """
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
            self._emit(Event.TELEMETRY_LIST_INITIALIZED, session=self.current_session, telemetries=self.current_session.telemetries)
        else:
            current_amount_of_telemetry = len(self.current_session.telemetries)
            for i in range(amount_of_pertinent_telemetry):
                packet_data = packet.car_telemetry_data[i]
                if i > current_amount_of_telemetry - 1:
                    new_telemetry = TelemetryManager.create(packet_data)
                    self.current_session.telemetries.append(new_telemetry)
                    self._emit(Event.TELEMETRY_CREATED, session=self.current_session, telemetry=new_telemetry)
                else:
                    changes = TelemetryManager.update(self.current_session.telemetries[i], packet_data)
                    participant = self.current_session.participants[i]
                    self._emit(Event.TELEMETRY_UPDATED, self.current_session.telemetries[i], changes, participant, self.current_session)

    """
    @emits CLASSIFICATION_CREATED
    @emits CLASSIFICATION_LIST_INITIALIZED
    @emits CLASSIFICATION_UPDATED
    """
    def _handle_received_final_classification_packet(self, packet:PacketFinalClassificationData):
        if not self.current_session:
            return # this should not happen
        if not self.current_session.final_classification:
            self.current_session.final_classification = [
                ClassificationManager.create(packet.classification_data[i])
                for i in range(packet.num_cars)
            ]
            self._emit(Event.CLASSIFICATION_LIST_INITIALIZED, session=self.current_session, final_classification=self.current_session.final_classification)
        else:
            current_amount_of_classification = len(self.current_session.final_classification)
            for i in range(packet.num_cars):
                packet_data = packet.classification_data[i]
                if i > current_amount_of_classification - 1:
                    new_classification = ClassificationManager.create(packet_data)
                    self._emit(Event.CLASSIFICATION_CREATED, session=self.current_session, final_classification=new_classification)
                    self.current_session.final_classification.append(new_classification)
                else:
                    changes = ClassificationManager.update(self.current_session.final_classification[i], packet_data)
                    if changes:
                        _logger.warning('!? final classification changed !?')
                        _logger.warning(changes)
                        self._emit(Event.CLASSIFICATION_UPDATED, session=self.current_session, changes=changes)

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
                    self._send_discord_message(Message(content=msg))
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
                            if not current_best or current_time < current_best:
                                setattr(self.current_session, session_attr, current_time)
                                msg = f'🕒 🟪 **{driver}**: nouveau meilleur {txts[key]} ! (`{self.current_session._format_time(sector_time)}`)'
                            else:
                                msg = f'🕒 🟩 **{driver}**: nouveau meilleur {txts[key]} personnel ! (`{self.current_session._format_time(sector_time)}`)'

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
                            self._send_discord_message(Message(content=msg))
                    # DON'T DO THE FOLLOWING IN RACE
                    if not self.current_session.session_type.is_race() and car_last_lap.driver_status not in (DriverStatus.in_pit, DriverStatus.out_lap):
                        if 'current_lap_invalid' in changes and car_last_lap.current_lap_invalid:
                            square_repr = '🟥🟥🟥'
                            msg = f'**{pilot}** : {square_repr}'
                            self._send_discord_message(Message(content=msg))
                        if lap_records and ('sector1_time_in_ms' in changes or 'sector2_time_in_ms' in changes) and not car_last_lap.current_lap_invalid:
                            pb_sector1 = lap_records.best_sector1_time
                            ob_sector1 = self.current_session.current_fastest_sector1

                            pb_sector2 = lap_records.best_sector2_time
                            ob_sector2 = self.current_session.current_fastest_sector2

                            square_repr = car_last_lap.get_squared_repr(pb_sector1, ob_sector1, pb_sector2, ob_sector2, None, None, None)

                            msg = f'**{pilot}** : {square_repr}'
                            self._send_discord_message(Message(content=msg))

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
                            self._send_discord_message(Message(content=msg))
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
                            self._send_discord_message(Message(content=msg))

                    # Compare with lap state last time pilot crossed the line...
                    old_lap_state = self.current_session.lap_state_last_start_of_lap[i]

                    # Notify position change if any
                    if old_lap_state and old_lap_state.car_position != new_lap.car_position:
                        position_change = new_lap.get_position_evolution(old_lap_state)
                        if position_change:
                            msg = f'{position_change} **{pilot}**'
                        self._send_discord_message(Message(content=msg))

                    # .. and update it
                    self.current_session.lap_state_last_start_of_lap[i] = LapManager.create(packet_data, len(car_laps))