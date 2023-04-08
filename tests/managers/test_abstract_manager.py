from dataclasses import dataclass
import unittest
from unittest.mock import Mock
from managers.abstract_manager import AbstractManager

from models.enums.track import Track


@dataclass
class Fake:
    boolean_field: bool = None
    enum_field: Track = None
    primitive_field: int = None


class FakeManager(AbstractManager):
    model = Fake
    primitive_fields = {'primitive_field': 'primitive_packet_field'}
    enum_fields = {
        'enum_field': (Track, 'enum_packet_field'),
    }
    bool_fields = {'boolean_field': 'boolean_packet_field'}


class AbstractManagerTest(unittest.TestCase):
    def test_create(self):
        packet = Mock(
            primitive_packet_field=12,
            boolean_packet_field=0,
            enum_packet_field=10
        )
        obj = FakeManager.create(packet)
        self.assertEqual(type(obj), Fake)
        self.assertFalse(obj.boolean_field)
        self.assertEqual(obj.enum_field, Track(10))
        self.assertEqual(obj.primitive_field, 12)

    def test_update(self):
        packet = Mock(
            primitive_packet_field=12,
            boolean_packet_field=0,
            enum_packet_field=10
        )
        obj = FakeManager.create(packet)

        upd_packet = Mock(
            primitive_packet_field=12,
            boolean_packet_field=0,
            enum_packet_field=9
        )
        changes = FakeManager.update(obj, upd_packet)
        self.assertEqual(len(changes), 1)
        self.assertIsNotNone(changes.get('enum_field'))
        self.assertEqual(changes['enum_field'].old, Track.spa)
        self.assertEqual(changes['enum_field'].actual, Track.hungaroring)

        upd_packet = Mock(
            primitive_packet_field=12,
            boolean_packet_field=1,
            enum_packet_field=9
        )
        changes = FakeManager.update(obj, upd_packet)
        self.assertEqual(len(changes), 1)
        self.assertIsNotNone(changes.get('boolean_field'))
        self.assertFalse(changes['boolean_field'].old)
        self.assertTrue(changes['boolean_field'].actual)

        upd_packet = Mock(
            primitive_packet_field=11,
            boolean_packet_field=1,
            enum_packet_field=9
        )
        changes = FakeManager.update(obj, upd_packet)
        self.assertEqual(len(changes), 1)
        self.assertIsNotNone(changes.get('primitive_field'))
        self.assertEqual(changes['primitive_field'].old, 12)
        self.assertEqual(changes['primitive_field'].actual, 11)

        changes = FakeManager.update(obj, packet)
        self.assertEqual(len(changes), 3)
        self.assertIsNotNone(changes.get('primitive_field'))
        self.assertIsNotNone(changes.get('boolean_field'))
        self.assertIsNotNone(changes.get('enum_field'))
        self.assertEqual(changes['primitive_field'].old, 11)
        self.assertEqual(changes['primitive_field'].actual, 12)
        self.assertFalse(changes['boolean_field'].actual)
        self.assertTrue(changes['boolean_field'].old)
        self.assertEqual(changes['enum_field'].actual, Track.spa)
        self.assertEqual(changes['enum_field'].old, Track.hungaroring)



