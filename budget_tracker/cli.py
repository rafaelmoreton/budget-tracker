# import typer
# from budget_tracker.parsers.parser import parse_statement

# app = typer.Typer(help="Personal Budget Tracker")

# @app.command()
# def parse(file_path: str):
#     """Parse a bank statement file"""
#     print(f"Parsing file: {file_path}")
#     # Call your existing parse logic here (even if incomplete)
#     result = parse_statement(file_path)  # This may error if not ready, but that's ok for now
#     print("Parse complete (placeholder)")

# def main():
#     app()

# if __name__ == "__main__":
#     main()