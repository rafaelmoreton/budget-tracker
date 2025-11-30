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
        
        
    def get_data(self) -> tuple[list[str], list[list[Any]]]:
        """
        Fetch ALL data from the worksheet in one single API call.
        
        Returns:
            headers: List of column names (first row)
            rows: List of rows (each row is a list of values)
        """

        all_values = self.worksheet.get_all_values()

        if not all_values:
            print(f"Warning: Worksheet '{self.worksheet_name}' is empty")
            return [], []

        headers = all_values[0]                    # first row = column names
        data_rows = all_values[1:]                 # everything else = actual data

        print(f"Loaded {len(data_rows)} rows from '{self.worksheet_name}' "
              f"with columns: {headers}")

        return headers, data_rows