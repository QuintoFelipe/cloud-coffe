<<<<<<< HEAD
from difflib import get_close_matches
from typing import Optional, List

def exact_item_match(query: str, items: List[str]) -> Optional[str]:
    q = query.lower().strip()
    if q in items:
        return q
    matches = get_close_matches(q, items, n=1, cutoff=0.7)
=======
from difflib import get_close_matches
from typing import Optional, List

def exact_item_match(query: str, items: List[str]) -> Optional[str]:
    q = query.lower().strip()
    if q in items:
        return q
    matches = get_close_matches(q, items, n=1, cutoff=0.7)
>>>>>>> bdfc648e5da2da83f3c00b80590671bad6c12a0e
    return matches[0] if matches else None