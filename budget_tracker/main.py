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
def generate_references(transactions_sheet: str = 'Lançamentos', references_sheet: str = 'Referências'):
    """Generate reference table from transactions and save to a new sheet."""
    
    print(f"Generating references from '{transactions_sheet}' to '{references_sheet}'")
    headers, data_rows = GoogleSheetsService(transactions_sheet).get_data()
    from budget_tracker.core.builder import generate_references
    references_data = generate_references(headers, data_rows)
    
    # Save to references sheet
    references_service = GoogleSheetsService()
    target_worksheet = references_service.ensure_worksheet(references_sheet)
    references_service.insert_data(target_worksheet, references_data)

    print("References generated successfully.")
    
@app.command()
def test_client():
    sheets = GoogleSheetsService('Página9')
    all_data = sheets.get_data()
    print("Current sheet content:", all_data) 

if __name__ == "__main__":
    app()