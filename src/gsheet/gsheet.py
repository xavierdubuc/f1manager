import os
from typing import List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
