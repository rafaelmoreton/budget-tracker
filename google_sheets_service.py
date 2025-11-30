import os
from typing import List, Any, Optional

import gspread
from dotenv import load_dotenv
from gspread.exceptions import APIError

load_dotenv()

class GoogleSheetsService:
    """
    A reusable service class for all Google Sheets operations in this project.
    """

    def __init__(
        self,
        worksheet_name: str,
        credentials_path: Optional[str] = None,
        spreadsheet_id: Optional[str] = None,
    ):
        """
        Initialize the service and connect to Google Sheets.

        Args:
            credentials_path: Path to service account credentials JSON (defaults to .env)
            spreadsheet_id: Google Sheets ID (defaults to .env)
            worksheet_name: Name of the worksheet/tab to use
        """
        self.worksheet_name = worksheet_name
        self.credentials_path = credentials_path or os.getenv("GSPREAD_CREDENTIALS")
        self.spreadsheet_id = spreadsheet_id or os.getenv("SPREADSHEET_ID")

        if not self.credentials_path or not self.spreadsheet_id:
            raise ValueError("Missing Google Sheets credentials or ID in .env")
        
        if not self.worksheet_name:
            raise ValueError("Missing worksheet name")

        self.client = gspread.service_account(filename=self.credentials_path)
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        self.worksheet = self.spreadsheet.worksheet(worksheet_name)

        print(f"Connected to spreadsheet: {self.spreadsheet.title} → {worksheet_name}")