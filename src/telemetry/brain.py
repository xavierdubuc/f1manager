import logging
from typing import Dict
import disnake

from disnake.ext import commands
from f1_23_telemetry.packets import (
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

from config.config import (Q1_RANKING_RANGE, Q2_RANKING_RANGE,
                           Q3_RANKING_RANGE, QUALI_RANKING_RANGE,
                           RACE_RANKING_RANGE)

from src.gsheet.gsheet import GSheet
from src.telemetry.event import Event

from src.telemetry.listeners.all_setups_listener import AllSetupsListener
from src.telemetry.listeners.best_lap_time_listener import BestLapTimeListener
from src.telemetry.listeners.classification_listener import ClassificationListener
from src.telemetry.listeners.dnf_listener import DNFListener
from src.telemetry.listeners.lap_start_listener import LapStartListener
from src.telemetry.listeners.noticeable_damage_listener import NoticeableDamageListener
from src.telemetry.listeners.penalty_listener import PenaltyListener
from src.telemetry.listeners.pit_listener import PitListener
from src.telemetry.listeners.position_change_listener import PositionChangeListener
from src.telemetry.listeners.qualification_sectors_listener import QualificationSectorsListener
from src.telemetry.listeners.safety_car_listener import SafetyCarListener
from src.telemetry.listeners.session_creation_listener import SessionCreationListener
from src.telemetry.listeners.telemetry_public_listener import TelemetryPublicListener
from src.telemetry.listeners.tyres_old_listener import TyresOldListener
from src.telemetry.listeners.weather_forecast_listener import WeatherForecastListener

from src.telemetry.managers.abstract_manager import Change
from src.telemetry.managers.car_status_manager import CarStatusManager
from src.telemetry.managers.car_setup_manager import CarSetupManager
from src.telemetry.managers.classification_manager import ClassificationManager
from src.telemetry.managers.damage_manager import DamageManager
from src.telemetry.managers.lap_manager import LapManager
from src.telemetry.managers.lap_record_manager import LapRecordManager
from src.telemetry.managers.participant_manager import ParticipantManager
from src.telemetry.managers.session_manager import SessionManager
from src.telemetry.managers.telemetry_manager import TelemetryManager

from src.telemetry.message import Channel, Message
from src.telemetry.models.enums.session_type import SessionType
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session


_logger = logging.getLogger(__name__)

LISTENER_CLASSES = [
    AllSetupsListener,
    BestLapTimeListener,
    ClassificationListener,
    DNFListener,
    LapStartListener,
    NoticeableDamageListener,
    PenaltyListener,
    PitListener,
    PositionChangeListener,
    QualificationSectorsListener,
    SafetyCarListener,
    SessionCreationListener,
    TelemetryPublicListener,
    TyresOldListener,
    WeatherForecastListener,
]


class Brain:
    def __init__(self, bot: commands.InteractionBot = None, championship_config:dict=None, sheet_name:str=None):
        self.current_session = None
        self.previous_sessions = []
        self.bot = bot
        self.last_weather_notified_at = None
        self.championship_config = championship_config
        self.listeners_by_event = {event: [] for event in Event}
        self.sheet_name = sheet_name
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

        elif packet_type == PacketCarStatusData:
            self._handle_received_status_packet(packet)

        elif packet_type == PacketCarTelemetryData:
            self._handle_received_telemetry_packet(packet)

        elif packet_type == PacketLapData:
            self._handle_received_lap_packet(packet)

        elif packet_type == PacketSessionHistoryData:
            self._handle_received_session_history_packet(packet)

        elif packet_type == PacketCarSetupData:
            self._handle_received_car_setup_packet(packet)

    def _send_discord_message(self, msg:Message, parent_msg:Message=None):
        if not self.bot:
            return
        if not self.bot.loop:
            return
        if msg.channel == Channel.BROADCAST:
            channels = [c for c in Channel if c != Channel.BROADCAST]
            for channel in channels:
                self._send_discord_message(Message(content=msg.content, channel=channel, file_path=msg.file_path), parent_msg=msg)
            return

        _logger.info(f'Following msg ({len(msg)} chars) to be sent to Discord ({msg.channel})')
        _logger.info(msg.content)

        discord_config = self.championship_config['discord'].get(msg.channel.value)
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
            for c in guild.channels:
                if c.name == discord_config['chann']:
                    channel = c
                    break
            if not channel:
                return

        where = channel
        if discord_config.get('use_thread', False) and channel.threads and len(channel.threads):
            where = channel.threads[-1]

        _logger.info(f'Message sent to "{guild.name}/#{channel.name}"')
        if msg.file_path:
            with open(msg.file_path, 'rb') as f:
                picture = disnake.File(f)
                self.bot.loop.create_task(where.send(msg.get_content(), file=picture))
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
            if changes:
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
                        if changes:
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
                    if changes:
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
                    if changes:
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
            self._send_ranking_to_gsheet(self.current_session)
        else:
            current_amount_of_classification = len(self.current_session.final_classification)
            at_least_one_change = False
            for i in range(packet.num_cars):
                packet_data = packet.classification_data[i]
                if i > current_amount_of_classification - 1:
                    at_least_one_change = True
                    new_classification = ClassificationManager.create(packet_data)
                    self._emit(Event.CLASSIFICATION_CREATED, session=self.current_session, final_classification=new_classification)
                    self.current_session.final_classification.append(new_classification)
                else:
                    changes = ClassificationManager.update(self.current_session.final_classification[i], packet_data)
                    if changes:
                        at_least_one_change = True
                        _logger.warning('!? final classification changed !?')
                        _logger.warning(changes)
                        self._emit(Event.CLASSIFICATION_UPDATED, session=self.current_session, changes=changes)
            if at_least_one_change:
                self._send_ranking_to_gsheet(self.current_session)

    """
    @emits LAP_RECORD_CREATED
    @emits LAP_RECORD_UPDATED
    """
    def _handle_received_session_history_packet(self, packet: PacketSessionHistoryData):
        if not self.current_session:
            return # this should not happen
        if not self.current_session.participants:
            return # this should not happen neither
        if not self.current_session.lap_records:
            self.current_session.lap_records = [None] * 20
        if not self.current_session.lap_records[packet.car_idx]:
            lap_record = LapRecordManager.create(packet)
            self.current_session.lap_records[packet.car_idx] = lap_record
            self._emit(Event.LAP_RECORD_CREATED, session=self.current_session, lap_record=lap_record)
        else:
            amount_of_participants = len(self.current_session.participants)
            if packet.car_idx >= amount_of_participants:
                return
            lap_record = self.current_session.lap_records[packet.car_idx]
            changes = LapRecordManager.update(lap_record, packet)
            participant = self.current_session.participants[packet.car_idx]

            if changes:
                if self.current_session.session_type.is_qualification():
                    self._keep_up_to_date_session_best_sectors(changes, participant)
                self._emit(Event.LAP_RECORD_UPDATED, lap_record, changes, participant, self.current_session)

    """
    @emits LAP_CREATED
    @emits LAP_UPDATED
    @emits LAP_START_CREATED
    """
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
                participant = self.current_session.participants[i]
                lap = LapManager.create(packet.lap_data[i], 0)
                self.current_session.laps.append([lap])
                self._emit(Event.LAP_CREATED, lap=lap, participant=participant, session=self.current_session)
                # We have to create again the lap as we want to store two different objects

                start_of_lap = LapManager.create(packet.lap_data[i], 0)
                self.current_session.lap_state_last_start_of_lap.append(start_of_lap)
                self._emit(Event.LAP_START_CREATED, lap=lap, participant=participant,
                           session=self.current_session, previous_lap=None)
        else:
            current_amount_of_lap = len(self.current_session.laps)
            for i in range(amount_of_pertinent_lap):
                packet_data = packet.lap_data[i]
                participant = self.current_session.participants[i]

                # We had no laps yet for this one
                if i > current_amount_of_lap - 1:
                    self.current_session.laps.append([])
                    self.current_session.lap_state_last_start_of_lap.append(None)

                car_laps = self.current_session.laps[i]
                car_last_lap = car_laps[-1] if car_laps else None

                # Same lap
                if car_last_lap and car_last_lap.current_lap_num == packet_data.current_lap_num:
                    changes = LapManager.update(car_last_lap, packet_data)
                    if changes:
                        self._emit(Event.LAP_UPDATED, lap=car_last_lap, changes=changes, participant=participant, session=self.current_session)
                # Pilot just crossed the line
                else:
                    # Add the new lap to the car's list of lap
                    new_lap = LapManager.create(packet_data, len(car_laps))
                    self._emit(Event.LAP_CREATED, lap=new_lap, participant=participant, session=self.current_session)
                    car_laps.append(new_lap)

                    # Update lap start
                    lap_start = LapManager.create(packet_data, len(car_laps))
                    previous_lap = self.current_session.lap_state_last_start_of_lap[i]
                    self.current_session.lap_state_last_start_of_lap[i] = lap_start
                    self._emit(Event.LAP_START_CREATED, lap=lap_start,
                               previous_lap=previous_lap,participant=participant,
                               session=self.current_session)

    """
    @emits CAR_STATUS_CREATED
    @emits CAR_STATUS_LIST_INITIALIZED
    @emits CAR_STATUS_UPDATED
    """
    def _handle_received_status_packet(self, packet:PacketCarStatusData):
        if not self.current_session:
            return # this should not happen
        if not self.current_session.participants:
            return # this should not happen neither
        if self.current_session.session_type == SessionType.clm:
            return # this has no sense
        pertinent_amount = len(self.current_session.participants)
        if not self.current_session.car_statuses:
            self.current_session.car_statuses = [
                CarStatusManager.create(packet.car_status_data[i])
                for i in range(pertinent_amount)
            ]
            self._emit(Event.CAR_STATUS_LIST_INITIALIZED, session=self.current_session, damages=self.current_session.car_statuses)
        else:
            current_amount = len(self.current_session.car_statuses)
            for i in range(pertinent_amount):
                participant = self.current_session.participants[i]
                packet_data = packet.car_status_data[i]
                if i > current_amount - 1:
                    new_car_status = CarStatusManager.create(packet_data)
                    self.current_session.car_statuses.append(new_car_status)
                    self._emit(Event.CAR_STATUS_CREATED, car_status=new_car_status, participant=participant, session=self.current_session)
                else:
                    changes = CarStatusManager.update(self.current_session.car_statuses[i], packet_data)
                    if changes:
                        self._emit(Event.CAR_STATUS_UPDATED, car_status=self.current_session.car_statuses[i], changes=changes, participant=participant, session=self.current_session)

    """
    @emits CAR_SETUP_CREATED
    @emits CAR_SETUP_LIST_INITIALIZED
    @emits CAR_SETUP_UPDATED
    """
    def _handle_received_car_setup_packet(self, packet:PacketCarSetupData):
        if not self.current_session:
            return # this should not happen
        if not self.current_session.participants:
            return # this should not happen neither
        # if self.current_session.session_type == SessionType.clm:
            # return # this has no sense
        pertinent_amount = len(self.current_session.participants)
        if not self.current_session.car_setups:
            self.current_session.car_setups = [
                CarSetupManager.create(packet.car_setups[i])
                for i in range(pertinent_amount)
            ]
            self._emit(Event.CAR_SETUP_LIST_INITIALIZED, session=self.current_session, setups=self.current_session.car_setups)
        else:
            current_amount = len(self.current_session.car_setups)
            for i in range(pertinent_amount):
                participant = self.current_session.participants[i]
                packet_data = packet.car_setups[i]
                if i > current_amount - 1:
                    new_car_setup = CarSetupManager.create(packet_data)
                    self.current_session.car_setups.append(new_car_setup)
                    self._emit(Event.CAR_SETUP_CREATED, car_setup=new_car_setup, participant=participant, session=self.current_session)
                else:
                    changes = CarSetupManager.update(self.current_session.car_setups[i], packet_data)
                    if changes:
                        self._emit(Event.CAR_SETUP_UPDATED, car_setup=self.current_session.car_setups[i], changes=changes, participant=participant, session=self.current_session)

    def _keep_up_to_date_session_best_sectors(self, changes:Dict[str, Change], participant:Participant = None):
        for sector in ('sector1', 'sector2', 'sector3'):
            if f'best_{sector}_time' in changes:
                current_best = getattr(self.current_session, f'current_fastest_{sector}')
                new_time = changes[f'best_{sector}_time'].actual
                print(sector, participant.name, new_time, current_best, changes)
                if not current_best or new_time < current_best:
                    setattr(self.current_session, f'current_fastest_{sector}', new_time)
                    self._emit(Event.BEST_SECTOR_UPDATED, session=self.current_session, participant=participant, sector=sector, now=new_time, old=current_best)

    def _send_ranking_to_gsheet(self, session:Session):
        if not self.sheet_name:
            _logger.info('No sheet name given, nothing will be sent')
            return
        if not session:
            _logger.error('Trying to send ranking of a not existing session !')
            return
        if not session.final_classification:
            _logger.error('Trying to send not existing ranking of a session !')
            return

        if session.session_type.is_race():
            range = RACE_RANKING_RANGE
        elif session.session_type.is_qualification():
            if session.session_type == SessionType.q1:
                session_type_str = 'Q1'
                range = Q1_RANKING_RANGE
            elif session.session_type == SessionType.q2:
                session_type_str = 'Q2'
                range = Q2_RANKING_RANGE
            elif session.session_type == SessionType.q3:
                session_type_str = 'Q3'
                range = Q3_RANKING_RANGE
            else:
                range = QUALI_RANKING_RANGE
                session_type_str = 'Qualifications'
            _logger.info(f'{session_type_str} ranking found, will be sent to google sheet !')
        else:
            _logger.info('Ranking will not be sent as this session type does not require it')

        final_ranking = session.get_formatted_final_ranking(delta_char='')
        for row in final_ranking:
            print('\t'.join(map(str, row)))

        g = GSheet()
        range_str = f"'{self.sheet_name}'!{range}"
        seasons = self.championship_config['seasons']
        season_id = list(seasons.keys())[-1]
        season = seasons[season_id]
        g.set_sheet_values(season['sheet'], range_str, final_ranking)
        _logger.info(f"Writing ranking above to sheet {season['sheet']}/{self.sheet_name}")
