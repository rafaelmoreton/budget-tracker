import os

from dotenv import load_dotenv
import gspread
from gspread.exceptions import WorksheetNotFound, APIError


load_dotenv()  # reads the .env file automatically

SERVICE_ACCOUNT_FILE = os.getenv("GSPREAD_CREDENTIALS")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

try:
    # Authenticate using the service account key
    google_client = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)

    # Open the spreadsheet by its ID
    spreadsheet = google_client.open_by_key(SPREADSHEET_ID)

    # Access the first worksheet (or use a specific one by name)
    worksheet = spreadsheet.sheet1
    # worksheet = spreadsheet.worksheet("Sheet2")  # example with name

    print(f"Successfully connected to spreadsheet: {spreadsheet.title}")

    # Example: Read all values from column A
    # column_a_values = worksheet.col_values(1)
    # print("\nFirst 5 values in Column A:")
    # print(column_a_values[:5])

    # Example: Write to a cell (uncomment to test)
    # worksheet.update("A10", [["Inserted via Python!"]])
    # print("Value written to A10")

    # Example: Append a new row (uncomment to test)
    # worksheet.append_row(["2025-11-30", "Test", 999])
    # print("New row appended")

except FileNotFoundError:
    print(f"Error: Credentials file not found at '{SERVICE_ACCOUNT_FILE}'")
    print("    Make sure the file exists and the path is correct.")
except APIError as e:
    print(f"Google API Error: {e}")
    print("    Common causes:")
    print("    • Service account email not shared with the spreadsheet (needs Editor access)")
    print("    • Invalid spreadsheet ID")
except Exception as e:
    print(f"Unexpected error: {e}")