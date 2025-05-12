import asyncio
import logging
from typing import TypedDict, List

from app.services.ai_model import extract_inventory_items
from app.services.sheets import get_inventory
from app.utils.fuzzy_match import exact_item_match

log = logging.getLogger(__name__)

class InvRow(TypedDict):
    item: str
    quantity: float
    unit: str
    minimum_level: float

def normalize_inventory(raw: List[dict]) -> List[InvRow]:
    """
    Turn each raw row (strings from Sheets) into typed InvRow,
    skipping any malformed rows.
    """
    norm: List[InvRow] = []
    for r in raw:
        try:
            norm.append({
                'item':           r['item'],
                'quantity':       float(r['quantity']),
                'unit':           r.get('unit',''),
                'minimum_level':  float(r['minimum_level'])
            })
        except Exception as e:
            log.error("Skipping bad inventory row %r: %s", r, e)
    return norm

async def inventory_agent(text: str) -> str:
    # 1) Load raw inventory & log for debugging
    raw = await asyncio.to_thread(get_inventory)
    log.info("DEBUG raw inventory rows: %r", raw)

    # 2) Normalize to correct types
    inv = normalize_inventory(raw)

    # 3) If the user requested specific items, use LLM + fuzzy match
    known = [r['item'] for r in inv]
    extracted = await extract_inventory_items(text, known)
    requested = [p.lower() for p in extracted]

    if requested:
        lines = []
        for name in requested:
            match = exact_item_match(name, [k.lower() for k in known])
            if match:
                row = next(r for r in inv if r['item'].lower() == match)
                lines.append(
                    f"{row['item']}: {row['quantity']}{row['unit']} "
                    f"(min {row['minimum_level']}{row['unit']})"
                )
            else:
                lines.append(f"Sorry, we don't have '{name}'.")
        return "\n".join(lines)

    # 4) Generic inventory query → list low-stock or “all above”
    low = [r for r in inv if r['quantity'] <= r['minimum_level']]
    if low:
        return (
            "Items below minimum:\n"
            + "\n".join(
                f"{r['item']}: {r['quantity']}{r['unit']} "
                f"(min {r['minimum_level']}{r['unit']})"
                for r in low
            )
        )

    return "All items are above minimum."
