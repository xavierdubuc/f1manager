from datetime import timedelta
import logging
from multiprocessing import Queue
from typing import Dict

from f1_24_telemetry.packets import (
    Packet,
    PacketCarDamageData,
    PacketCarTelemetryData,
    PacketCarStatusData,
    PacketCarSetupData,
    PacketLapData,
    PacketSessionData,
    PacketSessionHistoryData,
    PacketParticipantsData,
    PacketEventData,
    PacketFinalClassificationData,
    PacketMotionData,
    PacketTyreSetsData
)
from config.config import (Q1_RANKING_RANGE, Q2_RANKING_RANGE,
                           Q3_RANKING_RANGE, QUALI_RANKING_RANGE,
                           RACE_RANKING_RANGE, FASTEST_LAP_PILOT_CELL,
                           FASTEST_LAP_LAP_CELL, FASTEST_LAP_TIME_CELL)

from src.telemetry.listeners.tyreset_listener import TyreSetListener
from src.telemetry.managers.tyreset_manager import TyreSetManager
from src.telemetry.models.speed_trap_entry import SpeedTrapEntry
from src.media_generation.helpers.generator_type import GeneratorType
from src.media_generation.helpers.reader import Reader
from src.telemetry.models.lap import Lap
from src.gsheet.gsheet import GSheet
from src.telemetry.event import Event

from src.telemetry.listeners.all_setups_listener import AllSetupsListener
from src.telemetry.listeners.best_lap_time_listener import BestLapTimeListener
from src.telemetry.listeners.classification_listener import ClassificationListener
from src.telemetry.listeners.collision_listener import CollisionListener
from src.telemetry.listeners.dnf_listener import DNFListener
from src.telemetry.listeners.lap_start_listener import LapStartListener
from src.telemetry.listeners.noticeable_damage_listener import NoticeableDamageListener
from src.telemetry.listeners.overtake_listener import OvertakeListener
from src.telemetry.listeners.out_of_track_listener import OutOfTrackListener
from src.telemetry.listeners.penalty_listener import PenaltyListener
from src.telemetry.listeners.pit_listener import PitListener
from src.telemetry.listeners.position_change_listener import PositionChangeListener
from src.telemetry.listeners.speed_trap_listener import SpeedTrapListener
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
from src.telemetry.managers.motion_manager import MotionManager
from src.telemetry.managers.lap_record_manager import LapRecordManager
from src.telemetry.managers.participant_manager import ParticipantManager
from src.telemetry.managers.session_manager import SessionManager
from src.telemetry.managers.telemetry_manager import TelemetryManager

from src.telemetry.message import Message
from src.telemetry.models.enums.session_type import SessionType
from src.telemetry.models.participant import Participant
from src.telemetry.models.session import Session


_logger = logging.getLogger(__name__)

LISTENER_CLASSES = [
    AllSetupsListener,
    BestLapTimeListener,
    ClassificationListener,
    CollisionListener,
    DNFListener,
    LapStartListener,
    NoticeableDamageListener,
    OutOfTrackListener,
    OvertakeListener,
    PenaltyListener,
    PitListener,
    # PositionChangeListener,
    SpeedTrapListener,
    QualificationSectorsListener,
    SafetyCarListener,
    SessionCreationListener,
    TelemetryPublicListener,
    TyresOldListener,
    TyreSetListener,
    WeatherForecastListener,
]


class Brain:
    def __init__(self, queue: Queue = None, championship_config:dict=None, sheet_name:str=None, setup_data:dict=None):
        self.current_session = None
        self.previous_sessions = []
        self.queue = queue
        self.last_weather_notified_at = None
        self.championship_config = championship_config
        self.listeners_by_event = {event: [] for event in Event}
        self.sheet_name = sheet_name
        for Listener in LISTENER_CLASSES:
            listener = Listener(setup_data.get('emojis', {}))
            for event in Listener.SUBSCRIBED_EVENTS:
                self.listeners_by_event[event].append(listener)

    def handle_received_packet(self, packet: Packet):
        packet_type = type(packet)
        _logger.debug(f'Handling new {packet_type}')
        # TODO susbscribed packet and handle method or smthg

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

        elif packet_type == PacketEventData:
            self._handle_received_event_packet(packet)

        # elif packet_type == PacketMotionData:
        #     self._handle_received_motion_packet(packet)

        elif packet_type == PacketTyreSetsData:
            self._handle_received_tyreset_packet(packet)

    def _send_discord_message(self, msg:Message):
        if self.queue:
            self.queue.put(msg)
        else:
            _logger.info(msg.content)

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
    @emits MOTION_CREATED
    @emits MOTION_LIST_INITIALIZED
    @emits MOTION_UPDATED
    """
    def _handle_received_motion_packet(self, packet:PacketMotionData):
        if not self.current_session:
            return # this should not happen
        if not self.current_session.participants:
            return # this should not happen neither
        if self.current_session.session_type == SessionType.clm:
            return # this has no sense
        amount_of_pertinent_motions = len(self.current_session.participants)
        if not self.current_session.motions:
            self.current_session.motions = [
                MotionManager.create(packet.car_motion_data[i])
                for i in range(amount_of_pertinent_motions)
            ]
            self._emit(Event.MOTION_LIST_INITIALIZED, session=self.current_session, motions=self.current_session.motions)
        else:
            current_amount_of_motion = len(self.current_session.motions)
            for i in range(amount_of_pertinent_motions):
                packet_data = packet.car_motion_data[i]
                if i > current_amount_of_motion - 1:
                    new_motion = MotionManager.create(packet_data)
                    self.current_session.motions.append(new_motion)
                    self._emit(Event.MOTION_CREATED, session=self.current_session, motion=new_motion)
                else:
                    changes = MotionManager.update(self.current_session.motions[i], packet_data)
                    if changes:
                        participant = self.current_session.participants[i]
                        self._emit(Event.MOTION_UPDATED, self.current_session.motions[i], changes, participant, self.current_session)

    """
    @emits TYRESET_CREATED
    @emits TYRESET_UPDATED
    @emits PARTICIPANT_TYRESET_CREATED
    @emits PARTICIPANT_TYRESET_UPDATED
    """
    def _handle_received_tyreset_packet(self, packet:PacketTyreSetsData):
        if not self.current_session:
            return # this should not happen
        if not self.current_session.participants:
            return # this should not happen neither
        if not self.current_session.tyresets:
            self.current_session.tyresets = [None] * 20
        amount_of_participants = len(self.current_session.participants)
        if packet.car_idx >= amount_of_participants:
            return
        if not self.current_session.participants[packet.car_idx]:
            return # we wait to have the participant first
        participant = self.current_session.participants[packet.car_idx]

        if not self.current_session.tyresets[packet.car_idx]:
            self.current_session.tyresets[packet.car_idx] = []
            for tyreset_data in packet.tyre_set_data:
                tyreset = TyreSetManager.create(tyreset_data)
                self.current_session.tyresets[packet.car_idx].append(tyreset)
                self._emit(Event.TYRESET_CREATED, tyreset=tyreset, participant=participant, session=self.current_session)
            self._emit(Event.TYRESET_LIST_CREATED, tyresets=self.current_session.tyresets[packet.car_idx], participant=participant, session=self.current_session)
        else:
            tyresets = self.current_session.tyresets[packet.car_idx]
            has_changes = False
            tyreset_data = packet.tyre_set_data
            for i, tyreset in enumerate(tyresets):
                changes = TyreSetManager.update(tyreset, tyreset_data[i])
                if changes and ('fitted' in changes or 'available' in changes):
                    has_changes = True
                    self._emit(Event.TYRESET_UPDATED, tyreset, changes, participant, self.current_session)
            if has_changes:
                self._emit(Event.TYRESET_LIST_UPDATED, tyresets, participant, self.current_session)

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
                if self._same_lap(car_last_lap, packet_data):
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

    def _same_lap(self, lap:Lap, packet_data:PacketLapData):
        if not lap:
            return False
        return (
            lap.current_lap_num == packet_data.current_lap_num
            and not (lap.sector == 2 and packet_data.sector == 0)
        )

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

    def _handle_received_event_packet(self, packet:PacketEventData):
        supported = (
            'FTLP', 'RTMT', 'DRSE', 'DRSD', 'CHQF', 'RCWN',
            'SPTP', 'RDFL', 'OVTK', 'SCAR', 'COLL',
            #'SEND'  Inconsistently fired
        )
        event_code = ''.join([chr(i) for i in packet.event_string_code]).rstrip('\x00')
        if event_code in supported:
            if event_code == 'FTLP': # FASTEST LAP
                # {
                #     "lap_time": 79.941,
                #     "vehicle_idx": 16
                # }
                if self.current_session and self.current_session.participants:
                    fastest_lap = packet.event_details.fastest_lap
                    participant = self.current_session.participants[fastest_lap.vehicle_idx]
                    self._emit(Event.FASTEST_LAP, participant=participant, lap_time=fastest_lap.lap_time, session=self.current_session)
            if event_code == 'RTMT': # RETIREMENT
                _logger.info('RETIREMENT')
                _logger.info(packet.event_details.retirement.vehicle_idx)
            if event_code == 'DRSE': # DRS ENABLED
                _logger.info('---------- DRS ENABLED ! ----------')
            if event_code == 'DRSD': # DRS DISABLED
                _logger.info('---------- DRS DISABLED ! ----------')
            if event_code == 'CHQF': # CHEQUERED FLAG
                _logger.info('---------- CHEQUERED FLAG ! ----------')
            if event_code == 'RCWN': # RACE WINNER
                _logger.info('RACE WINNER')
                _logger.info(packet.event_details.race_winner.vehicle_idx)
            if event_code == 'SPTP': # SPEED TRAP TRIGGERED
                # {
                #     "fastest_speed_in_session": 326.359,
                #     "fastest_vehicle_idx_in_session": 0,
                #     "is_driver_fastest_in_session": 0,
                #     "overall_fastest_in_session": 0,
                #     "speed": 316.377,
                #     "vehicle_idx": 16
                # }
                speed_trap = packet.event_details.speed_trap
                if self.current_session and self.current_session.participants:
                    participant = self.current_session.participants[speed_trap.vehicle_idx]
                    fastest_participant = self.current_session.participants[speed_trap.fastest_vehicle_idx_in_session]
                    speed_trap_entry = SpeedTrapEntry(
                        participant=participant,
                        participant_speed=speed_trap.speed,
                        participant_is_fastest=speed_trap.overall_fastest_in_session,
                        speed_is_fastest_for_participant=speed_trap.is_driver_fastest_in_session,
                        fastest_speed_in_session=speed_trap.fastest_speed_in_session,
                        fastest_participant=fastest_participant,
                    )
                    self._emit(Event.SPEED_TRAP, speed_trap=speed_trap_entry, session=self.current_session)
            if event_code == 'RDFL': # RED FLAG
                _logger.info('---------- RED FLAG ! ----------')
            if event_code == 'OVTK': # OVERTAKE
                overtake = packet.event_details.overtake
                if self.current_session and self.current_session.participants:
                    overtaker = self.current_session.participants[overtake.overtaking_vehicle_idx]
                    overtaken = self.current_session.participants[overtake.being_overtaken_vehicle_idx]
                    self._emit(Event.OVERTAKE, overtaker=overtaker, overtaken=overtaken, session=self.current_session)
            if event_code == 'SCAR': # SAFETY CAR
                sc = packet.event_details.safety_car
                _logger.info('SAFETY CAR')
                _logger.info(sc.safety_car_type)
                _logger.info(sc.event_type)
            if event_code == 'COLL': # COLLISION
                collision = packet.event_details.collision
                if self.current_session and self.current_session.participants:
                    participant_1 = self.current_session.participants[collision.vehicle1_idx]
                    participant_2 = self.current_session.participants[collision.vehicle2_idx]
                    self._emit(Event.COLLISION, participant_1=participant_1, participant_2=participant_2, session=self.current_session)

    def _keep_up_to_date_session_best_sectors(self, changes:Dict[str, Change], participant:Participant = None):
        for sector in ('sector1', 'sector2', 'sector3'):
            if f'best_{sector}_time' in changes:
                current_best = getattr(self.current_session, f'current_fastest_{sector}')
                new_time = changes[f'best_{sector}_time'].actual
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

        g = GSheet()

        seasons = self.championship_config['seasons']
        season_id = list(seasons.keys())[-1]
        season = seasons[season_id]
        reader = Reader(GeneratorType.LINEUP, self.championship_config, season_id, self.sheet_name)
        config = reader.read()
        # FIXME print the ranking without any config if somehow reader is failing ?
        final_ranking = session.get_formatted_final_ranking(delta_char='', config=config)
        for row in final_ranking:
            print('\t'.join(map(str, row)))

        range_str = f"'{self.sheet_name}'!{range}"
        g.set_sheet_values(season['sheet'], range_str, final_ranking)
        _logger.info(f"Writing ranking above to sheet {season['sheet']}/{self.sheet_name}")

        # FASTEST LAP
        if session.current_fastest_lap:
            _logger.info('Writing fastest lap time in sheet ...')
            fastest_lap = timedelta(seconds=session.current_fastest_lap/1000)
            g.set_sheet_values(season['sheet'], f"'{self.sheet_name}'!{FASTEST_LAP_TIME_CELL}", [[session._format_time(fastest_lap)]])
        if session.current_fastest_lap_driver:
            _logger.info('Writing fastest lap driver in sheet ...')
            if not session.current_fastest_lap_driver.has_name:
                pilot = config.find_pilot(session.current_fastest_lap_driver)
                name = pilot.name
            else:
                name = str(session.current_fastest_lap_driver)
            g.set_sheet_values(season['sheet'], f"'{self.sheet_name}'!{FASTEST_LAP_PILOT_CELL}", [[name]])
        if session.current_fastest_lap_lap:
            _logger.info('Writing fastest lap # in sheet ...')
            g.set_sheet_values(season['sheet'], f"'{self.sheet_name}'!{FASTEST_LAP_LAP_CELL}", [[session.current_fastest_lap_lap]])
