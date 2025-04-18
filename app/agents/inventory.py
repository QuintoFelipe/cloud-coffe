import asyncio
from app.services.sheets import get_inventory
from app.utils.fuzzy_match import exact_item_match

async def inventory_agent(text: str) -> str:
    inv = await asyncio.to_thread(get_inventory)
    items = [row['item'].lower() for row in inv]
    for row in inv:
        match = exact_item_match(row['item'], items)
        if match and match in text.lower():
            return f"{row['item']}: {row['quantity']}{row.get('unit','')} (min {row.get('minimum_level','')}{row.get('unit','')})"
    low = [r for r in inv if r['quantity'] <= r.get('minimum_level',0)]
    if low:
        lines = [
            f"{r['item']}: {r['quantity']}{r.get('unit','')} (min {r.get('minimum_level','')}{r.get('unit','')})"
            for r in low
        ]
        return "Items below minimum:\n" + "\n".join(lines)
    return "All items are above minimum."