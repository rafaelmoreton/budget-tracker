import re
from typing import Dict, Any

# ----------------------------------------------------------------------
# Regexes
# ----------------------------------------------------------------------

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
    """Convert money string (e.g. '1.234,56' or '-3.080,88') to float."""
    return float(value.replace(".", "").replace(",", "."))


def extract_total(text: str) -> float | None:
    """Extract the official total from the line that contains 'Total da Fatura'."""
    for line in text.splitlines():
        if match := TOTAL_RE.search(line):
            return parse_money_value(match.group(1))
    return None


# ----------------------------------------------------------------------
# Core parser
# ----------------------------------------------------------------------
def parse_statement(text: str) -> Dict[str, Any]:
    """
    Parse a Brazilian credit-card statement, capturing all expenses and refunds.
    Returns a dict with transactions, captured total and the official total.
    """
    
    # Remove page markers and empty lines
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.startswith("Página")
    ]

    transactions = []
    current_category: str | None = None

    for line in lines:
        upper_line = line.upper()

        # --------------------------------------------------------------
        # 1. Lines that must be completely ignored
        # --------------------------------------------------------------
        if any(phrase in upper_line for phrase in [
            "DATA DESCRIÇÃO PAÍS VALOR",
            "SALDO FATURA ANTERIOR",
            "SUBTOTAL",
            "TOTAL DA FATURA"
        ]):
            continue

        # Specific previous month payment – ignore it
        if "PGTO DEBITO CONTA" in upper_line in line:
            continue

        # --------------------------------------------------------------
        # 2. Section headers → set category
        # --------------------------------------------------------------
        # Refunds / credits section
        if "PAGAMENTOS/CRÉDITOS" in upper_line:
            current_category = "Refunds"
            continue

        # Regular categories (Restaurantes, Serviços, Supermercados, etc.)
        if (re.match(r"^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s]*[A-Za-zÀ-ÿ]$", line)
                and "R$" not in line
                and "/" not in line):
            current_category = line.strip()
            continue

        # --------------------------------------------------------------
        # 3. Real transactions (start with DD/MM)
        # --------------------------------------------------------------
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

        # Uncomment for debugging unknown lines
        # print(f"[IGNORED] {line}")

    total_captured = sum(t["amount"] for t in transactions)
    expected_total = extract_total(text)

    return {
        "transactions": transactions,
        "total_captured": total_captured,
        "expected_total": expected_total
    }


# ----------------------------------------------------------------------
# Main / CLI
# ----------------------------------------------------------------------
def main() -> None:
    with open("data.txt", "r", encoding="utf-8") as f:
        text = f.read()

    result = parse_statement(text)

    print(f"Captured transactions : {len(result['transactions'])}")
    print(f"Sum of captured items : R$ {result['total_captured']:,.2f}")

    if result["expected_total"] is None:
        print("Warning: Could not find 'Total da Fatura' in the statement.")
        return

    print(f"Statement total (PDF) : R$ {result['expected_total']:,.2f}")

    if abs(result["total_captured"] - result["expected_total"]) < 0.01:
        print("SUCCESS! All values match perfectly.")
    else:
        diff = result["total_captured"] - result["expected_total"]
        print(f"FAILURE! Difference of R$ {diff:,.2f}")


if __name__ == "__main__":
    main()