import re
import csv
from typing import Dict, Any

# ----------------------------------------------------------------------
# Regexes
# ----------------------------------------------------------------------
BB_CREDIT_TRANSACTION_RE = re.compile(
    r"^(?P<date>\d{2}\.\d{2}\.\d{4})"
    r"(?P<description>.+?)"
    r"\s*(?P<country>[A-Z]{2})"
    r"\s+(?P<value>-?[\d.,]+)"
    r"\s+[\d.,]+$"
)

BB_CREDIT_TOTAL_RE = re.compile(
    r"^\s*Total\s+[\d\s]+\s+([\d.,]+)\s+[\d.,]+$"
)

TRANSACTION_RE = re.compile(
    r"^(?P<date>\d{2}/\d{2})\s+"
    r"(?P<description>.+?)"
    r"(?:\s+(?P<country>[A-Z]{2})\s+)?"
    r"\s*R\$\s*"
    r"(?P<value>-?[\d.,]+)$"
)

TOTAL_RE = re.compile(r"Total da Fatura\s+R\$\s*([\d.,]+)")


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def parse_money_value(value: str) -> float:
    """Convert Brazilian currency string (e.g. '1.234,56' or '-3.080,88') to float."""
    return float(value.replace(".", "").replace(",", "."))


def extract_total(text: str, total_re: re.Pattern) -> float | None:
    """Extract the official total from the 'Total da Fatura' line."""
    for line in text.splitlines():
        if match := total_re.search(line):
            return parse_money_value(match.group(1))
    return None

def is_bb_credit_card(text: str) -> bool:
    return (
        "SISBB - Sistema de Informações Banco do Brasil" in text
        and "Fatura do Cartão de Crédito" in text
    )


# ----------------------------------------------------------------------
# Core parsers
# ----------------------------------------------------------------------
def parse_statement(text: str) -> Dict[str, Any]:
    """
    Parse a Brazilian credit-card statement.
    Captures only current-period transactions (excludes previous balance and payment).
    Returns dict with transactions (expenses and refunds), captured total, and official total.
    """
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.startswith("Página")
    ]

    transactions = []
    current_category: str | None = None

    for line in lines:
        upper_line = line.upper()

        # 1. Lines that must be completely ignored
        if any(phrase in upper_line for phrase in [
            "DATA DESCRIÇÃO PAÍS VALOR",
            "SALDO FATURA ANTERIOR",
            "SUBTOTAL",
            "TOTAL DA FATURA"
        ]):
            continue

        # Specific previous-month payment — ignore completely
        if "PGTO DEBITO CONTA" in upper_line:
            continue

        # 2. Section: Refunds / Credits → category "Refunds"
        if "PAGAMENTOS/CRÉDITOS" in upper_line:
            current_category = "Refunds"
            continue

        # 3. Regular category headers (Restaurantes, Serviços, etc.)
        if (re.match(r"^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s]*[A-Za-zÀ-ÿ]$", line)
                and "R$" not in line
                and "/" not in line):
            current_category = line.strip()
            continue

        # 4. Real transaction — starts with DD/MM
        if match := TRANSACTION_RE.match(line):
            d = match.groupdict()
            amount = parse_money_value(d["value"])

            transactions.append({
                "date": d["date"],
                "description": d["description"].strip(),
                "category": current_category or "Uncategorized",
                "country": (d.get("country") or "BR").strip(),
                "amount": amount
            })
            continue

        # Optional debug: unknown lines
        # print(f"[IGNORED] {line}")

    total_captured = sum(t["amount"] for t in transactions)
    expected_total = extract_total(text, TOTAL_RE)

    return {
        "transactions": transactions,
        "total_captured": total_captured,
        "expected_total": expected_total
    }
    
def parse_bb_credit_card(text: str) -> Dict[str, Any]:
    """
    Parse Banco do Brasil (SISBB) credit card statement.
    Returns the same structure as parse_statement().
    """

    # 0. Extract only the DEMONSTRATIVO section
    raw_lines = []
    in_section = False

    for line in text.splitlines():
        if "DEMONSTRATIVO" in line:
            in_section = True
            continue

        if "RESUMO EM REAL" in line:
            break

        if in_section and line.strip():
            raw_lines.append(line.rstrip())

    # 1. Normalize lines (same intent as parse_statement)
    lines = [line.strip() for line in raw_lines]

    transactions = []
    current_category: str | None = None

    for line in lines:
        upper_line = line.upper()

        # 2. Lines that must be completely ignored
        if any(phrase in upper_line for phrase in [
            "DATA     TRANSAÇÕES",
            "SALDO FATURA ANTERIOR",
            "SUBTOTAL",
            "TOTAL",
            "----",
        ]):
            continue

        # 3. Refunds / credits section
        if "PAGAMENTOS/CRÉDITOS" in upper_line:
            current_category = "Refunds"
            continue

        # 4. Regular category headers
        if (
            re.match(r"^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s]*[A-Za-zÀ-ÿ]$", line)
            and not re.search(r"\d", line)
        ):
            current_category = line.strip()
            continue

        # 5. Real transaction — starts with DD.MM.YYYY
        if match := BB_CREDIT_TRANSACTION_RE.match(line):
            d = match.groupdict()
            amount = parse_money_value(d["value"])

            transactions.append({
                "date": d["date"],
                "description": d["description"].strip(),
                "category": current_category or "Uncategorized",
                "country": d["country"],
                "amount": amount,
            })
            continue

        # Optional debug
        # print(f"[IGNORED] {line}")
        # print(repr(line))

    total_captured = sum(t["amount"] for t in transactions)
    expected_total = extract_total(text, BB_CREDIT_TOTAL_RE)

    return {
        "transactions": transactions,
        "total_captured": total_captured,
        "expected_total": expected_total,
    }
        

# ----------------------------------------------------------------------
# CSV Export
# ----------------------------------------------------------------------
def format_brl(amount: float) -> str:
    """Format float to Brazilian currency string (e.g. 3048.82 → '3.048,82')."""
    formatted = f"{amount:,.2f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def export_to_csv(transactions: list[Dict[str, Any]], who_expended: str, filename: str = "budget_tracker/data/statement_transactions.csv") -> None:
    """
    Export parsed transactions to a CSV file.
    Includes a total row at the bottom.
    """
    fieldnames = ["date", "who", "description", "category", "country", "amount"]

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for t in transactions:
                writer.writerow({
                    "date": t["date"],
                    "who": who_expended,
                    "description": t["description"],
                    "category": t["category"],
                    "country": t["country"],
                    "amount": format_brl(t["amount"])
                })

        # Total row
        total_amount = sum(t["amount"] for t in transactions)
        writer.writerow({
            "date": "",
            "description": "TOTAL",
            "category": "",
            "country": "",
            "amount": format_brl(total_amount)
        })

    print(f"CSV exported successfully → {filename}")
    
    
# ----------------------------------------------------------------------
# Public function for the CLI — this replaces the old main()
# ----------------------------------------------------------------------
def parse_file(filepath: str, who_expended: str) -> dict:
    """Parse a credit card statement file and export CSV."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    if is_bb_credit_card(text):
        result = parse_bb_credit_card(text)
    else:
        result = parse_statement(text)

    print(f"Captured transactions : {len(result['transactions'])}")
    print(f"Sum of captured items : R$ {result['total_captured']:,.2f}")

    if result["expected_total"] is None:
        print("ERROR: Could not find 'Total da Fatura' in the statement.")
        return

    print(f"Statement total (PDF) : R$ {result['expected_total']:,.2f}")

    if abs(result["total_captured"] - result["expected_total"]) < 0.01:
        print("SUCCESS! All values match perfectly.")
        export_to_csv(result["transactions"], who_expended)
    else:
        diff = result["total_captured"] - result["expected_total"]
        print(f"FAILURE! Totals do not match. Difference: R$ {diff:,.2f}")
        print("CSV was NOT generated due to mismatch.")