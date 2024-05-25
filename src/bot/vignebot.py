from multiprocessing import Queue
from multiprocessing.connection import Connection
from disnake.ext import commands


class Vignebot(commands.InteractionBot):

    def connect_telemetry(self, queue: Queue, connection: Connection, championship_config: dict):
        self.connection = connection
        self.queue = queue
        self.championship_config = championship_config
