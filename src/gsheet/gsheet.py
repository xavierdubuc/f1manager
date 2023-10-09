import os
from typing import List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas

TOKEN_FILEPATH = 'config/token.json'
CREDENTIALS_FILEPATH = 'config/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GSheet:
    service = None

    def get_sheet_names(self, spreadsheet_id: str) -> list:
        res = self.get_service().get(spreadsheetId=spreadsheet_id).execute()
        return [s['properties']['title'] for s in res['sheets']]

    def get_sheet_values(self, spreadsheet_id: str, selection_range: str) -> list:
        return self.get_service().values().get(
            spreadsheetId=spreadsheet_id,
            range=selection_range
        ).execute()['values']

    def set_sheet_values(self, spreadsheet_id: str, selection_range: str, values: List[list]) -> dict:
        return self.get_service().values().update(
            spreadsheetId=spreadsheet_id,
            range=selection_range,
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()

    def get_service(self):
        if not self.service:
            self._init_service()
        return self.service

    def _init_service(self):
        
        creds = None
        if os.path.exists(TOKEN_FILEPATH):
            creds = Credentials.from_authorized_user_file(TOKEN_FILEPATH, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILEPATH, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILEPATH, 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('sheets', 'v4', credentials=creds)
            self.service = service.spreadsheets()
        except HttpError as err:
            print(err)

    def set_presence(self, spreadsheet_id: str, discord_name):
        pass

class PresenceGSheet(GSheet):
    def __init__(self, spreadsheet_id:str):
        self._gsheet = GSheet()
        self.spreadsheet_id = spreadsheet_id

    def set(self, discord_name:str, race_identifier: str, value:bool):
        str_value = 'Y' if value else 'N'
        values = self.get_sheet_values(self.spreadsheet_id, 'Presences!A1:M31')
        races = values[0]
        race_index = races.index(race_identifier)
        pilots = [v[0] for v in values[1:]]
        try:
            pilot_index = pilots.index(discord_name) + 1
        except ValueError:
            pilot_index = len(pilots) + 1
            self.set_sheet_values(self.spreadsheet_id, f'Presences!A{pilot_index+1}', [[discord_name]])
        self.set_sheet_values(self.spreadsheet_id, self._indexes_to_range(race_index, pilot_index), [[str_value]])

    def _indexes_to_range(self, race_index: int, pilot_index:int):
        column = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[race_index]
        row = pilot_index+1
        return f'Presences!{column}{row}'

    def get(self, race_identifier: str):
        values = self.get_sheet_values(self.spreadsheet_id, 'Presences!A1:M31')
        races = values[0]
        race_index = races.index(race_identifier)
        return {
            v[0]: v[race_index] if race_index < len(v) else False for v in values[1:]
        }