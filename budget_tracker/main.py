# parser.py (or main.py, or wherever you run the code)
from budget_tracker.sheets.client import GoogleSheetsService

def main() -> None:
    sheets = GoogleSheetsService('Página9')

    all_data = sheets.get_data()
    print("Current sheet content:", all_data)