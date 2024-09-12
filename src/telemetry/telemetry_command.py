import argparse


class Command(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument("ip", help="Ip address")
        self.add_argument("-c", "--championship", help="Championship concerned", dest='championship', default='FBRT')
        self.add_argument("--log-level", help="Log level", dest='log_level', default='info')
        self.add_argument('--final-sheet', help='Sheet to use to store final classification of last session', dest='sheet_name', default=None)
        self.add_argument("--no-twitch", help="No Twitch", dest='skip_twitch', action="store_true")

