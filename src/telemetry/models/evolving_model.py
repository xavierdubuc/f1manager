from dataclasses import dataclass
from datetime import timedelta
from f1_22_telemetry.packets import Packet

import logging

_logger = logging.getLogger(__name__)


@dataclass
class EvolvingModel:
    @staticmethod
    def _get_primitive_field_names():
        return {}

    @staticmethod
    def _get_enum_field_names():
        return {}

    @staticmethod
    def _get_bool_field_names():
        return {}

    @classmethod
    def create(cls, packet: Packet):
        self = cls()
        primitive_field_names = self._get_primitive_field_names()
        for field, packet_field in primitive_field_names.items():
            packet_value = getattr(packet, packet_field)
            setattr(self, field, packet_value)

        enum_field_names = self._get_enum_field_names()
        for field, (enum_class, packet_field) in enum_field_names.items():
            packet_value = getattr(packet, packet_field)
            setattr(self, field, enum_class(packet_value))

        bool_field_names = self._get_bool_field_names()
        for field, packet_field in bool_field_names.items():
            packet_value = getattr(packet, packet_field) != 0
            setattr(self, field, packet_value)

        return self

    def update(self, packet: Packet):
        primitive_field_names = self._get_primitive_field_names()
        for field, packet_field in primitive_field_names.items():
            curr_value = getattr(self, field)
            packet_value = getattr(packet, packet_field)
            if curr_value != packet_value:
                setattr(self, field, packet_value)
                

        enum_field_names = self._get_enum_field_names()
        for field, (enum_class, packet_field) in enum_field_names.items():
            curr_value = getattr(self, field).name
            packet_value = getattr(packet, packet_field)
            if getattr(self, field).value != packet_value:
                setattr(self, field, enum_class(packet_value))

        bool_field_names = self._get_bool_field_names()
        for field, packet_field in bool_field_names.items():
            packet_value = getattr(packet, packet_field) != 0
            if getattr(self, field) != packet_value:
                setattr(self, field, packet_value)

    def _primitive_value_changed(self, field, old_value, new_value):
        self._log(f'{field} changed, from {old_value} to "{new_value}"')

    def _enum_value_changed(self, field, old_value, new_value):
        self._log(f'{field} changed, from {old_value} to "{new_value}"')

    def _bool_value_changed(self, field, new_value):
        self._log(f'''{field} changed, now is "{'enabled' if new_value else 'disabled'}"''')

    def _log(self, txt: str):
        _logger.info(txt)

    def _warn(self, txt: str):
        _logger.warning(txt)

    def _format_time(self, seconds=0, milliseconds=0, with_hour=False):
        if milliseconds:
            seconds = milliseconds/1000
        if seconds > 60:
            no_tail = str(timedelta(seconds=seconds))[:-3]
            return no_tail if with_hour else no_tail[2:]
        else:
            return f'{seconds}s'
