import random
import asyncio
from datetime import datetime

from app.utils.fuzzy_match import exact_item_match
from app.services.sheets import (
    get_recipes,
    get_inventory,
    update_inventory,
    add_order,
    get_products
)
from app.services.ai_model import extract_order_items  # new import

async def order_agent(text: str) -> str:
    # 1) Ask Gemini to parse out all items
    items = await extract_order_items(text)
    # Normalize keys & lowercasing
    order_items: dict[str, int] = {
        item['product'].lower(): int(item.get('quantity', 1))
        for item in items
    }

    if not order_items:
        return "Sorry, I couldn’t detect any products in your order."

    # 2) Load recipes & inventory
    recipes = await asyncio.to_thread(get_recipes)
    inv = await asyncio.to_thread(get_inventory)
    inv_map = {row['item'].lower(): row['quantity'] for row in inv}

    # 3) Aggregate required ingredients
    needed_by_ing: dict[str, float] = {}
    for prod, qty in order_items.items():
        reqs = [r for r in recipes if r['item'].lower() == prod]
        if not reqs:
            return f"Sorry, we don't have {prod} right now."
        for r in reqs:
            ing = r['ingredient'].lower()
            needed = r['quantity_per_unit'] * qty
            needed_by_ing[ing] = needed_by_ing.get(ing, 0) + needed

    # 4) Stock check
    for ing, needed in needed_by_ing.items():
        if inv_map.get(ing, 0) < needed:
            return f"Sorry, not enough {ing} for that order."

    # 5) Pricing map
    products = await asyncio.to_thread(get_products)
    price_map = {p['product'].lower(): p['price_unit_dolars'] for p in products}

    # 6) Commit to Sheets in background
    def perform_order_tasks():
        # deduct inventory
        for ing, needed in needed_by_ing.items():
            update_inventory(ing, inv_map[ing] - needed)

        # shared order ID & timestamp
        order_id = f"#{random.randint(1000,9999)}"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # one row per line‑item
        for prod, qty in order_items.items():
            total_price = price_map.get(prod, 0) * qty
            add_order(order_id, prod, timestamp, qty, total_price)

        return order_id

    order_id = await asyncio.to_thread(perform_order_tasks)

    # 7) Build the user response
    lines = []
    grand_total = 0.0
    for prod, qty in order_items.items():
        unit = price_map.get(prod, 0)
        total = unit * qty
        grand_total += total
        lines.append(f"{qty}×{prod}: ${total:.2f}")

    return (
        f"Order {order_id} placed successfully:\n"
        + "\n".join(lines)
        + f"\nGrand Total: ${grand_total:.2f}"
    )
