from typing import List, Dict, Any, Tuple
from collections import defaultdict

def generate_references(headers: List[str], data_rows: List[List[Any]]) -> List[List[str]]:
    """
    Generate a reference table from transaction data.
    Maps unique (description, comment, who) to a single category.
    Raises ValueError if multiple categories found for the same key.
    Assumes headers include: 'Descrição', 'Comentário', 'Quem', 'Categoria'
    """
    if not data_rows:
        raise ValueError("Missing transactions data.")

    # Map column names to indices for readability
    col_description = headers.index('Descrição') if 'Descrição' in headers else None
    col_comment = headers.index('Comentário') if 'Comentário' in headers else None
    col_who = headers.index('Quem') if 'Quem' in headers else None
    col_category = headers.index('Categoria') if 'Categoria' in headers else None

    # Use a dict to group by normalized key: (description, comment, who) -> list of (category, original_row)
    reference_map: Dict[Tuple[str, str, str], List[str]] = defaultdict(list)

    for row in data_rows:
        category = row[col_category]
        if not category:
            continue
        description = row[col_description] if isinstance(col_description, int) else ""
        comment = row[col_comment] if isinstance(col_comment, int) else ""
        who = row[col_who] if isinstance(col_who, int) else ""

        key = (description, comment, who)
        reference_map[key].append(category)

    # Check for conflicts and build the reference table if there are none
    reference_table = [['Descrição', 'Comentário', 'Quem', 'Categoria']]
    conflicts = []
    
    for key, categories_list in reference_map.items():
        
        description, comment, who = key
        
        categories = set(categories_list)
        if len(categories) > 1: # There should be only one category for each unique key
            # Build error message with divergent records
            conflict_msg = f"Conflict found for key {key}: multiple categories detected:\n"
            for cat in categories:
                conflict_msg += f" - Category '{cat}' in row: {key}\n"
            
            conflicts.append(conflict_msg)
            continue

        # No conflict: use the first entry's original values and category
        category = categories_list[0]
        reference_table.append([description, comment, who, category])
    
    if conflicts:
        full_error_message = "\n".join(conflicts)
        raise ValueError(full_error_message)

    return reference_table