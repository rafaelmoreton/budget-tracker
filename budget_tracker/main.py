import typer
from budget_tracker.parsers.parser import parse_file
from budget_tracker.sheets.client import GoogleSheetsService

app = typer.Typer()

@app.callback()
def callback():
    """
    Budget tracker
    """
    
@app.command()
def parse(file_path: str):
    """Parse a bank statement file"""
    print(f"Parsing file: {file_path}")
    parse_file(file_path)
    print("Parse complete")
    
@app.command()
def test_client():
    sheets = GoogleSheetsService('Página9')
    all_data = sheets.get_data()
    print("Current sheet content:", all_data) 

if __name__ == "__main__":
    app()