import argparse


class Command(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument("type", help="Type de visuel (results, lineup, presentation, fastest, details)")
        self.add_argument("-s", "--sheet", help="Name of the Excel sheet to use", dest='sheet', default=None)
        self.add_argument("-o", "--output", help="Output file to use", dest='output', default=None)
        self.add_argument("-i", "--input", help="Input file to use (use 'gsheet:TIMESHEET_ID' for google sheet (replace TIMESHEET_ID with the id of the sheet of course)", dest='input', default='gsheet')
        self.add_argument("-a", "--season", help="Season (only used in standings)", dest='season', default=5)
        self.add_argument("-m", "--metric", help="Metric to use to sort rankings (only used in standings)", dest='metric', default='Total')

