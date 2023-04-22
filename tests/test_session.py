from copy import copy
from datetime import timedelta
import unittest
from src.telemetry.models.classification import Classification
from src.telemetry.models.enums.game_mode import GameMode
from src.telemetry.models.enums.result_status import ResultStatus
from src.telemetry.models.enums.session_length import SessionLength
from src.telemetry.models.enums.session_type import SessionType
from src.telemetry.models.enums.track import Track
from src.telemetry.models.enums.tyre import Tyre
from src.telemetry.models.participant import Participant

from src.telemetry.models.session import Session


class SessionTest(unittest.TestCase):
    def setUp(self):
        self.session = Session(
            session_type=SessionType.clm,
            track=Track.spa,
            game_mode=GameMode.online_custom,
            session_length=SessionLength.long,
            time_of_day=12
        )

    def test_get_formatted_final_ranking_row(self):
        p = Participant(name="Xionhearts")
        classification = Classification(
            position=1,
            result_status=ResultStatus.retired,
            best_lap_time_in_ms= 72000, # 1min12
            tyre_stints_visual=[Tyre.soft, Tyre.hard],
            total_race_time= 2700, # 45min
            penalties_time=10
        )
        res = self.session._get_formatted_final_ranking_row(classification, p)
        self.assertListEqual(res, [1, 'Xionhearts', timedelta(seconds=72)])

        self.session.session_type = SessionType.race
        res = self.session._get_formatted_final_ranking_row(classification, p)
        self.assertListEqual(res, [1, 'Xionhearts', 'NT', 'SH', timedelta(seconds=72)])

        classification.result_status=ResultStatus.dnf
        res = self.session._get_formatted_final_ranking_row(classification, p)
        self.assertListEqual(res, [1, 'Xionhearts', 'NT', 'SH', timedelta(seconds=72)])

        classification.result_status=ResultStatus.not_classified
        res = self.session._get_formatted_final_ranking_row(classification, p)
        self.assertListEqual(res, [1, 'Xionhearts', 'NT', 'SH', timedelta(seconds=72)])

        classification.result_status=ResultStatus.dsq
        res = self.session._get_formatted_final_ranking_row(classification, p)
        self.assertListEqual(res, [1, 'Xionhearts', 'DSQ', 'SH', timedelta(seconds=72)])

        classification.result_status=ResultStatus.finished
        res = self.session._get_formatted_final_ranking_row(classification, p)
        self.assertListEqual(res, [1, 'Xionhearts', timedelta(seconds=2710), 'SH', timedelta(seconds=72)])


    def test__format_time(self):
        t = timedelta(seconds = 0.596)
        self.assertEqual(self.session._format_time(t), '0.596')

        t = timedelta(seconds = 9, microseconds=1000)
        self.assertEqual(self.session._format_time(t), '9.001')

        t = timedelta(seconds = 30)
        self.assertEqual(self.session._format_time(t), '30.000')

        t = timedelta(seconds = 59)
        self.assertEqual(self.session._format_time(t), '59.000')

        t = timedelta(seconds = 59.086)
        self.assertEqual(self.session._format_time(t), '59.086')

        t = timedelta(seconds = 61.086)
        self.assertEqual(self.session._format_time(t), '1:01.086')

        t = timedelta(seconds = 610.086)
        self.assertEqual(self.session._format_time(t), '10:10.086')

    def test___eq__(self):
        s1 = Session(
            session_type=SessionType.clm,
            track=Track.spa,
            game_mode=GameMode.online_custom,
            session_length=SessionLength.long,
            time_of_day=12
        )
        self.assertNotEqual(s1, SessionType.clm)
        s2 = copy(s1)
        s2.time_of_day = 14
        self.assertEqual(s1,s2)

        s2.session_type = SessionType.fp1
        self.assertNotEqual(s1, s2)
        s2.session_type = SessionType.clm
        self.assertEqual(s1, s2)

        s2.track = Track.bahrain
        self.assertNotEqual(s1, s2)
        s2.track = Track.spa
        self.assertEqual(s1, s2)

        s2.game_mode = GameMode.career_22
        self.assertNotEqual(s1, s2)
        s2.game_mode = GameMode.online_custom
        self.assertEqual(s1, s2)

        s2.session_length = SessionLength.full
        self.assertNotEqual(s1, s2)
        s2.session_length = SessionLength.long
        self.assertEqual(s1, s2)