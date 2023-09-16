import argparse


class Command(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument("type", help="Type de visuel (lineup, presentation, results, pilot)")
        self.add_argument("-c", "--championship", help="Championship concerned", dest='championship', default='FBRT')
        self.add_argument("-a", "--season", help="Season (only used in standings)", dest='season', default=None, type=int)
        self.add_argument("-o", "--output", help="Output file to use", dest='output', default=None)
        self.add_argument("-s", "--sheet", help="Name of the Excel sheet to use", dest='sheet', default=None)
        self.add_argument("-m", "--metric", help="Metric to use to sort rankings (only used in standings)", dest='metric', default='Total')
        self.add_argument("-i", "--identifier", help="Identifier for a sub part (like the pseudo for a pilot)", dest='identifier', default=None)

