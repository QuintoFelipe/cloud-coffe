import asyncio
from app.services.sheets import get_inventory
from app.utils.fuzzy_match import exact_item_match

async def inventory_agent(text: str) -> str:
    inv = await asyncio.to_thread(get_inventory)
    text_lower = text.lower()

    # Extraer lista de nombres de ítems
    item_names = [row['item'].lower() for row in inv]

    # Intentar encontrar un ítem específico mencionado en el texto del usuario
    for word in text_lower.split():
        match = exact_item_match(word, item_names)
        if match:
            row = next((r for r in inv if r['item'].lower() == match), None)
            if row:
                return f"{row['item']}: {row['quantity']}{row.get('unit','')} (min {row.get('minimum_level','')}{row.get('unit','')})"

    # Si no se detectó un ítem específico, mostrar los bajos en stock
    low_stock = [
        r for r in inv if r['quantity'] <= r.get('minimum_level', 0)
    ]
    if low_stock:
        lines = [
            f"{r['item']}: {r['quantity']}{r.get('unit','')} (min {r.get('minimum_level','')}{r.get('unit','')})"
            for r in low_stock
        ]
        return "Items below minimum:\n" + "\n".join(lines)

    return "All items are above minimum."
