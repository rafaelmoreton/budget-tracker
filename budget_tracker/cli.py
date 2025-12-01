import typer

app = typer.Typer(help="Personal Budget Tracker")

@app.command()
def parse(file_path: str):
    """Parse a bank statement file"""
    typer.echo(f"Received file path: {file_path}")
    typer.echo("Parse command works! Next step: real parsing logic.")


def main():
    app()

if __name__ == "__main__":
    main()