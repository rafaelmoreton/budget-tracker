# budget_tracker/cli.py
import typer
from budget_tracker.parsers.parser import parse_file

app = typer.Typer(help="Personal Budget Tracker")


@app.command()
def parse(file_path: str):
    """Parse a bank statement file"""
    typer.echo(f"Received file path: {file_path}")

    result = parse_file(file_path)

    typer.echo("Parsing complete!")
    typer.echo(f"Found {len(result['transactions'])} transactions")  # simple feedback

def main():
    app()

if __name__ == "__main__":
    main()