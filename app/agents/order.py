import random
import asyncio
import re
from datetime import datetime
from app.utils.fuzzy_match import exact_item_match
from app.services.sheets import (
    get_recipes,
    get_inventory,
    update_inventory,
    add_order,
    get_products
)

async def order_agent(text: str) -> str:
    # 1) Load recipes & product list
    recipes = await asyncio.to_thread(get_recipes)
    product_names = {r['item'].lower() for r in recipes}

    # 2) Parse out all (product, quantity) mentions
    txt = text.lower()
    order_items: dict[str, int] = {}
    for prod in product_names:
        # look for "<number>? <product>[s]?" 
        pattern = rf'\b(\d+)?\s*{re.escape(prod)}s?\b'
        m = re.search(pattern, txt)
        if m:
            qty = int(m.group(1)) if m.group(1) else 1
            order_items[prod] = order_items.get(prod, 0) + qty

    if not order_items:
        return "Sorry, I couldn’t detect any products in your order."

    # 3) Build inventory requirements (aggregate per ingredient)
    inv = await asyncio.to_thread(get_inventory)
    inv_map = {i['item'].lower(): i['quantity'] for i in inv}

    needed_by_ing: dict[str, float] = {}
    for prod, qty in order_items.items():
        reqs = [r for r in recipes if r['item'].lower() == prod]
        for r in reqs:
            ing = r['ingredient'].lower()
            needed = r['quantity_per_unit'] * qty
            needed_by_ing[ing] = needed_by_ing.get(ing, 0) + needed

    # 4) Check stock
    for ing, needed in needed_by_ing.items():
        if inv_map.get(ing, 0) < needed:
            return f"Sorry, not enough {ing} for that order."

    # 5) Get pricing
    products = await asyncio.to_thread(get_products)
    price_map = {p['product'].lower(): p['price_unit_dolars'] for p in products}

    # 6) Perform updates in background thread
    def perform_order_tasks():
        # deduct inventory
        for ing, needed in needed_by_ing.items():
            new_qty = inv_map[ing] - needed
            update_inventory(ing, new_qty)

        # single shared order ID & timestamp
        order_id = f"#{random.randint(1000,9999)}"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # append one row per product
        for prod, qty in order_items.items():
            unit_price = price_map.get(prod, 0)
            total_price = unit_price * qty
            add_order(order_id, prod, timestamp, qty, total_price)

        return order_id

    order_id = await asyncio.to_thread(perform_order_tasks)

    # 7) Build response
    lines = []
    grand_total = 0.0
    for prod, qty in order_items.items():
        unit = price_map.get(prod, 0)
        total = unit * qty
        grand_total += total
        lines.append(f"{qty}×{prod}: ${total:.2f}")

    resp = (
        f"Order {order_id} placed successfully:\n"
        + "\n".join(lines)
        + f"\nGrand Total: ${grand_total:.2f}"
    )
    return resp
