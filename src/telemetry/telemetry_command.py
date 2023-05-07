import argparse


class Command(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument("ip", help="Ip address")
        self.add_argument("--log-level", help="Log level", dest='log_level', default='info')
        self.add_argument('--final-sheet', help='Sheet to use to store final classification of last session', dest='sheet_name', default=None)
        self.add_argument('g','--discord-guild', help='Discord guild id', dest='discord_guild', default=None)
        self.add_argument('d','--discord-channel', help='Discord channel id', dest='discord_channel', default=None)

