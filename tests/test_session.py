from copy import copy
import unittest
from models.enums.game_mode import GameMode
from models.enums.session_length import SessionLength
from models.enums.session_type import SessionType
from models.enums.track import Track

from models.session import Session

class SessionTest(unittest.TestCase):
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