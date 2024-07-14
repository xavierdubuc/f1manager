from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import List
import tabulate

import disnake
from f1_24_telemetry.listener import TelemetryListener
from f1_24_telemetry.packets import PacketParticipantsData, PacketSessionData, PacketLapData, PacketTimeTrialData
from src.telemetry.models.enums.track import Track
from src.bot.vignebot import Vignebot
from src.gsheet.gsheet import GSheet
from src.media_generation.models.circuit import Circuit
from src.media_generation.data import circuits as CIRCUITS

SPREADSHEET_ID = '1NS4tFVoOpVBygCR-4Fj5-FjUULW5dXJcOAs0eMg1hxg'
TOC_SHEET_NAME = 'TOC'
CIRCUITS_VALUES_SHEET_NAME = '_circuits'
CIRCUITS_VALUES_SHEET_RANGE = 'A3:B28'
MESSAGE_ID_RANGE = 'B1'
TIME_TRIAL_RANGE = 'A3:F50'

DISCORD_GUILD_ID = 923505034778509342
DISCORD_CHANNEL_ID = 1257435341732712521

TABULATE_FORMAT = 'simple_outline'

_logger = logging.getLogger(__name__)

def get_participant_name(packet: PacketParticipantsData, index=0):
    name = packet.participants[index].name
    return name.decode('utf-8') if isinstance(name, bytes) else name

def format_time(obj:timedelta):
    if obj == timedelta(0):
        return '--:--.---'
    minutes = obj.seconds//60
    minutes_str = f'{obj.seconds//60}:' if minutes > 0 else ''
    seconds = obj.seconds%60
    seconds_str = str(seconds).zfill(2) if minutes > 0 else seconds
    return f'{minutes_str}{seconds_str}.{str(obj.microseconds//1000).zfill(3)}'


@dataclass
class TimeTrialManager:
    bot: Vignebot
    gsheet: GSheet = GSheet()
    guild: disnake.Guild = None
    channel: disnake.TextChannel = None
    circuits: List[Circuit] = None

    def __post_init__(self):
        cell_range = f'{CIRCUITS_VALUES_SHEET_NAME}!{CIRCUITS_VALUES_SHEET_RANGE}'
        circuit_values = self.gsheet.get_sheet_values(SPREADSHEET_ID, cell_range)
        self.circuits_idx = {
            name: CIRCUITS.get(name, Circuit(name, name, None, None, city))
            for name, city in circuit_values
        }
        self.circuits = list(self.circuits_idx.values())

    async def setup(self):
        self.guild = await self.bot.fetch_guild(DISCORD_GUILD_ID)
        _logger.info(f'GUILD: {self.guild}')
        self.channel = await self.guild.fetch_channel(DISCORD_CHANNEL_ID)
        _logger.info(f'CHANNEL: {self.channel}')

    async def reset(self):
        _logger.info('Create not existing sheets...')
        self.create_not_existing_sheets()
        _logger.info('Create not existing messages...')
        await self.create_not_existing_messages()

    def fetch_from_game(self, ip='192.168.1.15'):
        # TODO TEST ME
        listener = TelemetryListener(port=20777, host=ip)
        circuit = None
        personal_name = None
        rival_name = None
        best_laps = {}
        state = 'CIRCUIT'
        try:
            _logger.info('Waiting for session packet to get circuit...')
            while True:
                packet = listener.get()
                if state == 'CIRCUIT':
                    if isinstance(packet, PacketSessionData):
                        track = Track(packet.track_id)
                        circuit = self.circuits_idx[track.get_name()]
                        _logger.info(f'"{circuit.name}" circuit selected !')
                        state = 'TIME_TRIAL'

                if state == 'TIME_TRIAL':
                    if isinstance(packet, PacketTimeTrialData):
                        print(packet._fields)
                        pb = packet.personal_best_data_set
                        rival = packet.rival_data_set
                        state = 'PARTICIPANT'

                if state == 'PARTICIPANT':
                    if isinstance(packet, PacketParticipantsData):
                        # ADDING PB
                        personal_name = get_participant_name(packet, pb.car_idx)
                        if personal_name and not best_laps[personal_name]:
                            time_values = [
                                timedelta(seconds=pb.sector1_time_in_ms/1000),
                                timedelta(seconds=pb.sector2_time_in_ms/1000),
                                timedelta(seconds=pb.sector3_time_in_ms/1000),
                                timedelta(seconds=pb.lap_time_in_ms/1000),
                            ]
                            best_laps[personal_name] = time_values
                            _logger.info(f'Added {format_time(time_values[3])} of "{personal_name}"')

                        # ADDING RIVAL
                        rival_name = get_participant_name(packet, rival.car_idx)
                        if rival_name and not best_laps[rival_name]:
                            time_values = [
                                timedelta(seconds=rival.sector1_time_in_ms/1000),
                                timedelta(seconds=rival.sector2_time_in_ms/1000),
                                timedelta(seconds=rival.sector3_time_in_ms/1000),
                                timedelta(seconds=rival.lap_time_in_ms/1000),
                            ]
                            best_laps[rival_name] = time_values
                            _logger.info(f'Added {format_time(time_values[3])} of "{rival_name}"')
                        state = 'TIME_TRIAL'
        except KeyboardInterrupt:
            pass

        if not circuit or not best_laps:
            _logger.error('No circuit or no lap time registered !')
            return
        values = sorted([(k, s1, s2, s3, lap) for k, (s1, s2, s3, lap) in best_laps.items()], key=lambda x: x[4])
        values_str = [
            (i+1, k, format_time(s1), format_time(s2), format_time(s3), format_time(lap))
            for i, (k, s1, s2, s3, lap) in enumerate(values)
        ]
        _logger.info('Fetched ranking that will be stored :')
        _logger.info(values_str)
        self._update_circuit_sheet(circuit, values_str)

    # ##################
    # CIRCUIT (SHEET)
    # ##################

    def create_not_existing_sheets(self):
        all_sheets = self.gsheet.get_sheet_names(SPREADSHEET_ID)
        for circuit in self.circuits:
            if circuit.get_identifier() not in all_sheets:
                _logger.info(f'Creating sheet for circuit {circuit}')
                self._create_circuit_sheet(circuit)
            else:
                _logger.info(f'Sheet already exists for circuit {circuit}')

    def _create_circuit_sheet(self, circuit: Circuit):
        self.gsheet.add_sheet(SPREADSHEET_ID, circuit.get_identifier())
        self._set_circuit_sheet_headers_values(circuit)

    def _set_circuit_sheet_headers_values(self, circuit: Circuit):
        cell_range = f'{circuit.get_identifier()}!A1:C6'
        self.gsheet.set_sheet_values(SPREADSHEET_ID, cell_range, [
            ['Message ID', '', ''],
            ['Position', 'Pilot', 'S1', 'S2', 'S3', 'Time']
        ])

    def _get_circuit_ranking(self, circuit: Circuit) -> List[List[str]]:
        cell_range = f'{circuit.get_identifier()}!{TIME_TRIAL_RANGE}'
        return self.gsheet.get_sheet_values(SPREADSHEET_ID, cell_range)

    # ##########
    # MESSAGES
    # ##########

    async def create_not_existing_messages(self):
        for circuit in self.circuits:
            await self._create_circuit_message_if_not_existing(circuit)
        await self._create_toc_message_if_not_existing()

    async def _get_message(self, identifier) -> disnake.Message:
        message_id_cell_range = f'{identifier}!{MESSAGE_ID_RANGE}'
        values = self.gsheet.get_sheet_values(SPREADSHEET_ID, message_id_cell_range)
        message_id = self._to_msg_id(values)
        if not message_id:
            return None
        _logger.debug(f'"{identifier}" message id #{message_id}"...')
        message = await self.channel.fetch_message(message_id)
        if not message:
            return None
        _logger.debug(f'"{identifier}" message found')
        return message

    async def update_all_circuit_messages(self):
        for circuit in self.circuits:
            await self.update_circuit_message(circuit)

    async def _create_message_if_not_existing(self, identifier:str, creation_function:callable, *args, **kwargs) -> disnake.Message:
        message = await self._get_message(identifier)
        if not message:
            _logger.debug(f'No "{identifier}" message')
            return await creation_function(*args, **kwargs)
        return message

    def _store_message_id(self, identifier: str, message_id: str):
        cell_range = f'{identifier}!{MESSAGE_ID_RANGE}'
        self.gsheet.set_sheet_values(SPREADSHEET_ID, cell_range,
                                     self._to_sheet_values(message_id))

    # ##########
    # TOC (MESSAGE)
    # ##########

    async def _get_toc_message(self) -> disnake.Message:
        return await self._get_message(TOC_SHEET_NAME)

    async def _create_toc_message_if_not_existing(self) -> disnake.Message:
        return await self._create_message_if_not_existing(TOC_SHEET_NAME, self._create_toc_message)

    async def _create_toc_message(self) -> disnake.Message:
        _logger.debug('Creating TOC message...')
        limit_first_msg = len(self.circuits) // 2

        # 1st message
        parts = [
            '# MENU'
        ]
        for circuit in self.circuits[:limit_first_msg]:
            circuit_msg = await self._get_circuit_message(circuit)
            parts.append(
                f'- {circuit.emoji} [{circuit.name}]({circuit_msg.jump_url})'
            )
        msg_content =  '\n'.join(parts)
        msg = await self.channel.send(msg_content)

        # 2nd message
        parts = []
        for circuit in self.circuits[limit_first_msg:]:
            circuit_msg = await self._get_circuit_message(circuit)
            parts.append(
                f'- {circuit.emoji} [{circuit.name}]({circuit_msg.jump_url})'
            )
        msg2_content =  '\n'.join(parts)
        msg2 = await self.channel.send(msg2_content) # TODO store this id too

        _logger.debug('TOC message sent')
        self._store_message_id(TOC_SHEET_NAME, msg.id)
        _logger.debug('TOC message ID stored in spreadsheet')
        return msg

    # ##################
    # CIRCUIT (MESSAGE)
    # ##################

    async def _get_circuit_message(self, circuit: Circuit) -> disnake.Message:
        return await self._get_message(circuit.get_identifier())

    async def _create_circuit_message_if_not_existing(self, circuit:Circuit) -> disnake.Message:
        return await self._create_message_if_not_existing(circuit.get_identifier(), self._create_circuit_message, circuit)

    async def _create_circuit_message(self, circuit: Circuit):
        _logger.debug(f'Creating message for {circuit.city} ...')
        msg_txt = self._get_circuit_message_content(circuit)
        msg = await self.channel.send(msg_txt)
        self._store_message_id(circuit.get_identifier(), msg.id)

    def _update_circuit_sheet(self, circuit: Circuit, values: List[List[str]]):
        cell_range = f'{circuit.get_identifier()}!{TIME_TRIAL_RANGE}'
        self.gsheet.set_sheet_values(SPREADSHEET_ID, cell_range, values)

    async def update_circuit_message(self, circuit: Circuit):
        _logger.info(f'Updating "{circuit.name}" message from sheet {circuit.get_identifier()}')
        msg = await self._get_circuit_message(circuit)
        new_content = self._get_circuit_message_content(circuit)
        await msg.edit(new_content)

    def _get_circuit_message_content(self, circuit: Circuit):
        msg_parts = [
            f'## {circuit.emoji} {circuit.city.upper()} {circuit.emoji}',
            '```'
        ]
        circuit_ranking = self._get_circuit_ranking(circuit)
        if circuit_ranking:
            msg_parts.append(tabulate.tabulate(circuit_ranking, tablefmt=TABULATE_FORMAT))
        else:
            msg_parts.append('Aucun temps encore synchronisé')
        msg_parts.append('```')
        return '\n'.join(msg_parts)

    # ########
    # HELPERS
    # ########
    def _to_sheet_values(self, msg_id:int) -> List[List[str]]:
        return [[str(msg_id)]]

    def _to_msg_id(self, values:List[List[str]]) -> int:
        if not values:
            return None
        if len(values) == 0:
            return None
        if len(values[0][0]) == 0:
            return None
        return int(values[0][0])
