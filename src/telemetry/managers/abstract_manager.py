from typing import Dict
from f1_24_telemetry.packets import Packet


class Change:
    def __init__(self, old, actual):
        self.old = old
        self.actual = actual

    def __str__(self) -> str:
        return f'{str(self.old)} -> {str(self.actual)}'

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        return self.old == other.old and self.actual == other.actual


class AbstractManager:
    model = object

    primitive_fields = {}

    enum_fields = {}

    bool_fields = {}

    @classmethod
    def create(cls, packet: Packet):
        self = cls.model()
        for field, packet_field in cls.primitive_fields.items():
            packet_value = getattr(packet, packet_field)
            setattr(self, field, packet_value)

        for field, (enum_class, packet_field) in cls.enum_fields.items():
            packet_value = getattr(packet, packet_field)
            setattr(self, field, enum_class(packet_value))

        for field, packet_field in cls.bool_fields.items():
            packet_value = getattr(packet, packet_field) != 0
            setattr(self, field, packet_value)

        return self

    @classmethod
    def update(cls, model, packet: Packet) -> Dict[str, Change]:
        changes = {}
        for field, packet_field in cls.primitive_fields.items():
            curr_value = getattr(model, field)
            packet_value = getattr(packet, packet_field)
            if curr_value != packet_value:
                changes[field] = Change(actual=packet_value, old=curr_value)
                setattr(model, field, packet_value)

        for field, (enum_class, packet_field) in cls.enum_fields.items():
            curr_value = getattr(model, field)
            packet_value = enum_class(getattr(packet, packet_field))

            if curr_value != packet_value:
                changes[field] = Change(actual=packet_value, old=curr_value)
                setattr(model, field, packet_value)

        for field, packet_field in cls.bool_fields.items():
            curr_value = getattr(model, field)
            packet_value = getattr(packet, packet_field) != 0
            if curr_value != packet_value:
                changes[field] = Change(actual=packet_value, old=curr_value)
                setattr(model, field, packet_value)

        return changes
