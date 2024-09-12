import argparse
from src.logging import setup as setup_logging
from src.bot import run


class Command(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument("--no-twitch", help="No Twitch", dest='skip_twitch', action="store_true")


args = Command().parse_args()
setup_logging()
run(skip_twitch=args.skip_twitch)
