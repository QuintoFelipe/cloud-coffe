import asyncio
from app.services.ai_model import extract_inventory_items
from app.services.sheets import get_inventory
from app.utils.fuzzy_match import exact_item_match

async def inventory_agent(text: str) -> str:
    # 1) Load current inventory
    inv = await asyncio.to_thread(get_inventory)
    known_products = [row['item'] for row in inv]

    # 2) Ask Gemini what the user wants (any language)
    extracted = await extract_inventory_items(text, known_products)
    requested = [p.lower() for p in extracted]

    # 3) If Gemini found specific items, report those
    if requested:
        lines = []
        for name in requested:
            # fuzzy‑match to tolerate slight mismatches
            match = exact_item_match(name, [i.lower() for i in known_products])
            if match:
                row = next(r for r in inv if r['item'].lower() == match)
                qty = row['quantity']
                unit = row.get('unit','')
                minl = row.get('minimum_level','')
                lines.append(f"{row['item']}: {qty}{unit} (min {minl}{unit})")
            else:
                lines.append(f"Sorry, we don't have '{name}'.")
        return "\n".join(lines)

    # 4) FALLBACK: original behavior when no specific product mentioned
    #    (show low‑stock items or generic "all above")
    item_names = [row['item'].lower() for row in inv]
    text_lower = text.lower()
    for word in text_lower.split():
        match = exact_item_match(word, item_names)
        if match:
            row = next(r for r in inv if r['item'].lower() == match)
            return f"{row['item']}: {row['quantity']}{row.get('unit','')} (min {row.get('minimum_level','')}{row.get('unit','')})"

    low_stock = [r for r in inv if r['quantity'] <= r.get('minimum_level', 0)]
    if low_stock:
        lines = [
            f"{r['item']}: {r['quantity']}{r.get('unit','')} (min {r.get('minimum_level','')}{r.get('unit','')})"
            for r in low_stock
        ]
        return "Items below minimum:\n" + "\n".join(lines)

    return "All items are above minimum."
