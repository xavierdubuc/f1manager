import ctypes
import unittest
from unittest.mock import Mock, call, patch
from f1_22_telemetry.packets import (
    PacketSessionData,
    PacketParticipantsData,
    ParticipantData,
    FinalClassificationData,
    PacketFinalClassificationData,
    PacketCarDamageData,
    PacketCarTelemetryData,
    PacketLapData,
    LapData
)

from brain import Brain
from models.classification import Classification
from models.enums.nationality import Nationality
from models.enums.team import Team
from models.enums.track import Track
from models.enums.tyre import Tyre
from models.enums.tyre_compound import TyreCompound
from models.participant import Participant
from models.session import Session


class BrainTest(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.brain = Brain()

    @patch('brain.Brain._handle_received_lap_packet')
    @patch('brain.Brain._handle_received_telemetry_packet')
    @patch('brain.Brain._handle_received_damage_packet')
    @patch('brain.Brain._handle_received_final_classification_packet')
    @patch('brain.Brain._handle_received_participants_packet')
    @patch('brain.Brain._handle_received_session_packet')
    def test_handle_received_packet(self, patch_session, patch_participant, patch_classification, patch_damage, patch_telemetry, patch_lap):
        session_packet = PacketSessionData()
        participant_packet = PacketParticipantsData()
        classification_packet = PacketFinalClassificationData()
        damage_packet = PacketCarDamageData()
        telemetry_packet = PacketCarTelemetryData()
        lap_packet = PacketLapData()

        self.brain.handle_received_packet(session_packet)
        self.brain.handle_received_packet(participant_packet)
        self.brain.handle_received_packet(classification_packet)
        self.brain.handle_received_packet(damage_packet)
        self.brain.handle_received_packet(telemetry_packet)
        self.brain.handle_received_packet(lap_packet)

        patch_session.assert_called_once_with(session_packet)
        patch_participant.assert_called_once_with(participant_packet)
        patch_classification.assert_called_once_with(classification_packet)
        patch_damage.assert_called_once_with(damage_packet)
        patch_telemetry.assert_called_once_with(telemetry_packet)
        patch_lap.assert_called_once_with(lap_packet)

    @patch('managers.session_manager.SessionManager.update')
    @patch('managers.session_manager.SessionManager.create')
    def test__handle_received_session_packet(self, patched_create, patched_update):
        # no current session
        session = Session(track=Track.spa)
        patched_create.return_value = session
        packet = PacketSessionData(track_id=10)

        self.brain._handle_received_session_packet(packet)
        patched_create.assert_called_once_with(packet)
        self.assertEqual(self.brain.current_session, session)
        self.assertListEqual(self.brain.previous_sessions, [])
        patched_update.assert_not_called()

        # session didn't change
        patched_create.reset_mock()
        new_session = Session(track=Track.spa)
        patched_create.return_value = new_session

        self.brain._handle_received_session_packet(packet)
        patched_create.assert_called_once_with(packet)
        self.assertEqual(self.brain.current_session, session)
        self.assertListEqual(self.brain.previous_sessions, [])
        patched_update.assert_called_once_with(session, packet)

        # session changed
        patched_create.reset_mock()
        patched_update.reset_mock()
        new_session = Session(track=Track.hungaroring)
        packet = PacketSessionData(track_id=Track.hungaroring.value)
        patched_create.return_value = new_session

        self.brain._handle_received_session_packet(packet)
        patched_create.assert_called_once_with(packet)
        self.assertEqual(self.brain.current_session, new_session)
        self.assertListEqual(self.brain.previous_sessions, [session])
        patched_update.assert_not_called()

    @patch('managers.participant_manager.ParticipantManager.update')
    @patch('managers.participant_manager.ParticipantManager.create')
    def test__handle_received_participants_packet(self, patched_create, patched_update):
        xion = Participant(name="Xion")
        prolactron = Participant(name="Prolactron")
        cid = Participant(name="Cid")
        participants_data = [
            ParticipantData(
                ai_controlled=False, driver_id=255, network_id=1,
                team_id=Team.alfa_romeo.value, my_team=0, race_number=2,
                nationality=Nationality.belgian.value, name=b'Xionhearts', your_telemetry=1
            ),
            ParticipantData(
                ai_controlled=False, driver_id=255, network_id=2,
                team_id=Team.ferrari.value, my_team=0, race_number=26,
                nationality=Nationality.turkish.value, name=b'Prolactron', your_telemetry=1
            ),
        ]
        packet = PacketParticipantsData(num_active_cars=2, participants=(ParticipantData * 22)(*participants_data))

        self.brain._handle_received_participants_packet(packet)
        patched_create.assert_not_called()
        patched_update.assert_not_called()
        patched_create.side_effect = [xion, prolactron, cid]

        self.brain.current_session = Session()

        self.brain._handle_received_participants_packet(packet)
        self.assertEqual(patched_create.call_count, 2)
        self.assertEqual(str(patched_create.call_args_list[0][0][0]), str(packet.participants[0]))
        self.assertEqual(str(patched_create.call_args_list[1][0][0]), str(packet.participants[1]))
        patched_update.assert_not_called()
        self.assertListEqual(self.brain.current_session.participants, [xion, prolactron])

        patched_create.reset_mock()
        patched_update.reset_mock()
        participants_data[1].team_id = Team.aston_martin.value
        participants_data.append(
            ParticipantData(
                ai_controlled=False, driver_id=255, network_id=3,
                team_id=Team.mercedes.value, my_team=0, race_number=16,
                nationality=Nationality.belgian.value, name=b'FBRT_CiD16', your_telemetry=1
            )
        )
        new_packet = PacketParticipantsData(num_active_cars=3, participants=(ParticipantData * 22)(*participants_data))

        self.brain._handle_received_participants_packet(new_packet)
        self.assertEqual(patched_update.call_count, 2)
        self.assertEqual(patched_update.call_args_list[0][0][0], xion)
        self.assertEqual(patched_update.call_args_list[1][0][0], prolactron)
        self.assertEqual(str(patched_update.call_args_list[0][0][1]), str(new_packet.participants[0]))
        self.assertEqual(str(patched_update.call_args_list[1][0][1]), str(new_packet.participants[1]))
        patched_create.assert_called_once()
        self.assertEqual(str(patched_create.call_args[0][0]), str(new_packet.participants[2]))

    @patch('managers.classification_manager.ClassificationManager.update')
    @patch('managers.classification_manager.ClassificationManager.create')
    def test__handle_received_classification_packet(self, patched_create, patched_update):
        xion = Classification(position=1)
        prolactron = Classification(position=2)
        cid = Classification(position=3)
        classification_data = [
            FinalClassificationData(
                position=1, num_laps=12, grid_position=2, points=25,
                num_pit_stops=1, result_status=3, best_lap_time_in_ms=1000, total_race_time=12000,
                penalties_time=0, num_penalties=0, num_tyre_stints=2,
                tyre_stints_actual=(ctypes.c_uint8*8)(TyreCompound.c1.value, TyreCompound.c2.value, 0, 0, 0, 0, 0, 0),
                tyre_stints_visual=(ctypes.c_uint8*8)(Tyre.soft.value, Tyre.medium.value, 0, 0, 0, 0, 0, 0),
                tyre_stints_end_laps=(ctypes.c_uint8*8)(1, 255, 0, 0, 0, 0, 0, 0)
            ),
            FinalClassificationData(
                position=2, num_laps=12, grid_position=3, points=18,
                num_pit_stops=1, result_status=3, best_lap_time_in_ms=2000, total_race_time=14000,
                penalties_time=0, num_penalties=0, num_tyre_stints=2,
                tyre_stints_actual=(ctypes.c_uint8*8)(TyreCompound.c1.value, TyreCompound.c2.value, 0, 0, 0, 0, 0, 0),
                tyre_stints_visual=(ctypes.c_uint8*8)(Tyre.soft.value, Tyre.medium.value, 0, 0, 0, 0, 0, 0),
                tyre_stints_end_laps=(ctypes.c_uint8*8)(1, 255, 0, 0, 0, 0, 0, 0)
            ),
        ]
        packet = PacketFinalClassificationData(num_cars=2, classification_data=(
            FinalClassificationData * 22)(*classification_data))

        self.brain._handle_received_final_classification_packet(packet)
        patched_create.assert_not_called()
        patched_update.assert_not_called()

        patched_create.side_effect = [xion, prolactron, cid]
        self.brain.current_session = Session()

        self.brain._handle_received_final_classification_packet(packet)
        self.assertEqual(patched_create.call_count, 2)
        self.assertEqual(str(patched_create.call_args_list[0][0][0]), str(packet.classification_data[0]))
        self.assertEqual(str(patched_create.call_args_list[1][0][0]), str(packet.classification_data[1]))
        patched_update.assert_not_called()
        self.assertListEqual(self.brain.current_session.final_classification, [xion, prolactron])

        patched_create.reset_mock()
        patched_update.reset_mock()
        classification_data[1].position = 3
        classification_data.append(
            FinalClassificationData(
                position=2, num_laps=12, grid_position=12, points=18,
                num_pit_stops=1, result_status=3, best_lap_time_in_ms=2000, total_race_time=14000,
                penalties_time=0, num_penalties=0, num_tyre_stints=2,
                tyre_stints_actual=(ctypes.c_uint8*8)(TyreCompound.c1.value, TyreCompound.c2.value, 0, 0, 0, 0, 0, 0),
                tyre_stints_visual=(ctypes.c_uint8*8)(Tyre.soft.value, Tyre.medium.value, 0, 0, 0, 0, 0, 0),
                tyre_stints_end_laps=(ctypes.c_uint8*8)(1, 255, 0, 0, 0, 0, 0, 0)
            ),
        )
        new_packet = PacketFinalClassificationData(num_cars=3, classification_data=(
            FinalClassificationData * 22)(*classification_data))

        self.brain._handle_received_final_classification_packet(new_packet)
        self.assertEqual(patched_update.call_count, 2)
        self.assertEqual(patched_update.call_args_list[0][0][0], xion)
        self.assertEqual(patched_update.call_args_list[1][0][0], prolactron)
        self.assertEqual(str(patched_update.call_args_list[0][0][1]), str(new_packet.classification_data[0]))
        self.assertEqual(str(patched_update.call_args_list[1][0][1]), str(new_packet.classification_data[1]))
        patched_create.assert_called_once()
        self.assertEqual(str(patched_create.call_args[0][0]), str(new_packet.classification_data[2]))

    @patch('managers.damage_manager.DamageManager.update')
    @patch('managers.damage_manager.DamageManager.create')
    def test__handle_received_damage_packet(self, patched_create, patched_update):
        pass  # TODO (flemme car pareil que les autres en vrai)

    @patch('managers.telemetry_manager.TelemetryManager.update')
    @patch('managers.telemetry_manager.TelemetryManager.create')
    def test__handle_received_telemetry_packet(self, patched_create, patched_update):
        pass  # TODO (flemme car pareil que les autres en vrai)

    @patch('managers.lap_manager.LapManager.update')
    @patch('managers.lap_manager.LapManager.create')
    def _test__handle_received_lap_packet_no_part(self, patched_create, patched_update):
        packet = PacketLapData(lap_data=[])
        self.brain._handle_received_lap_packet(packet)
        patched_create.assert_not_called()
        patched_update.assert_not_called()

        self.brain.current_session = Session()
        self.brain._handle_received_lap_packet(packet)
        patched_create.assert_not_called()
        patched_update.assert_not_called()

        self.brain.current_session.participants = []
        self.brain._handle_received_lap_packet(packet)
        patched_create.assert_not_called()
        patched_update.assert_not_called()

    @patch('managers.lap_manager.LapManager.update')
    @patch('managers.lap_manager.LapManager.create')
    def _test__handle_received_lap_packet_no_lap_yet(self, patched_create, patched_update):
        self.brain.current_session = Session()
        self.brain.current_session.participants = [
            Participant(name="Xion"), Participant(name="DimDim")
        ]
        packet = PacketLapData(lap_data=(LapData * 22)(
            LapData(current_lap_num=1), LapData(current_lap_num=1)
        ))
        self.brain._handle_received_lap_packet(packet)
        