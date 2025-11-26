import re
from typing import List, Dict

TRANSACTION_RE = re.compile(
    r"^(?P<date>\d{2}/\d{2})\s+"
    r"(?P<description>.*?)\s+"
    r"(?P<country>[A-Z]{2})?\s*"
    r"R\$\s*(?P<value>-?\d{1,3}(?:\.\d{3})*,\d{2})$"
)
    
def parse_statement(text: str) -> List[Dict]:
    lines = [
        l.strip()
        for l in text.splitlines()
        if l.strip() and not l.startswith("Página")
    ]

    results = []
    current_category = None

    for line in lines:
        # Is it a category header?
        if re.match(r"^[A-Za-zÀ-ÿ].+$", line) and not re.match(r"^\d{2}/\d{2}", line):
            # Exclude "Data Descrição País Valor" or "Subtotal..."
            if "R$" not in line and not line.startswith("Data"):
                current_category = line
            continue

        # Try match transaction
        match = TRANSACTION_RE.match(line)
        if match:
            d = match.groupdict()
            results.append({
                "date": d["date"],
                "description": d["description"],
                "category": current_category,
                "country": d["country"],
                "amount": parse_brl(d["value"]),
            })

    return results

def parse_brl(value: str) -> float:
    """Convert Brazilian currency format to float."""
    return float(value.replace(".", "").replace(",", "."))

with open("data.txt", "r", encoding="utf-8") as f:
    text = f.read()
    
print(parse_statement(text))