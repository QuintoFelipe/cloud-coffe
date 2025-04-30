from asyncio.log import logger
import random
import asyncio
import re
from datetime import datetime

from app.services.ai_model import extract_order_items
from app.services.sheets import (
    get_recipes,
    get_inventory,
    update_inventory,
    add_order,
    get_products
)
from app.services.notifications import send_low_stock_alert 



async def order_agent(text: str, chat_id: str) -> str:
    # 1) LLM extraction (handles any language & spelled‑out numbers)
    raw_items = await extract_order_items(text)
    order_items: dict[str, int] = {}
    for itm in raw_items:
        prod = itm.get('product', '').lower()
        qty = int(itm.get('quantity', 1))
        if prod:
            order_items[prod] = order_items.get(prod, 0) + qty

    # 2) DIGITS‑ONLY fallback (e.g. "2 latte")
    if not order_items:
        recipes = await asyncio.to_thread(get_recipes)
        product_names = {r['item'].lower() for r in recipes}
        lowered = text.lower()
        for prod in product_names:
            pattern = rf'\b(\d+)\s+{re.escape(prod)}s?\b'
            for m in re.finditer(pattern, lowered):
                qty = int(m.group(1))
                order_items[prod] = order_items.get(prod, 0) + qty

    if not order_items:
        return "Sorry, I couldn’t detect any products in your order."

    # 3) Load recipes & inventory
    recipes = await asyncio.to_thread(get_recipes)
    inv = await asyncio.to_thread(get_inventory)
    inv_map = {row['item'].lower(): row['quantity'] for row in inv}

    # 4) Aggregate needed ingredients
    needed_by_ing: dict[str, float] = {}
    for prod, qty in order_items.items():
        reqs = [r for r in recipes if r['item'].lower() == prod]
        if not reqs:
            return f"Sorry, we don't have {prod} right now."
        for r in reqs:
            ing = r['ingredient'].lower()
            needed = r['quantity_per_unit'] * qty
            needed_by_ing[ing] = needed_by_ing.get(ing, 0) + needed

    # 5) Stock check
    for ing, needed in needed_by_ing.items():
        if inv_map.get(ing, 0) < needed:
            return f"Sorry, not enough {ing} for that order."

    # 6) Pricing map
    products = await asyncio.to_thread(get_products)
    price_map = {p['product'].lower(): p['price_unit_dolars'] for p in products}

    # 7) Commit to Sheets in background
    def perform_order_tasks():
        # deduct inventory
        for ing, needed in needed_by_ing.items():
            update_inventory(ing, inv_map[ing] - needed)

        # single shared order ID & timestamp
        order_id = f"#{random.randint(1000,9999)}"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # one row per line‑item
        for prod, qty in order_items.items():
            total_price = price_map.get(prod, 0) * qty
            add_order(order_id, prod, timestamp, qty, total_price)

        return order_id

    order_id = await asyncio.to_thread(perform_order_tasks)

   # 8) After a successful order, trigger low-stock alert if needed
   # Always pass the chat_id as a string key
    cid_str = str(chat_id)
    logger.info(f"order_agent: scheduling low-stock alert to chat {cid_str}")
    # run in background
    asyncio.create_task(
        asyncio.to_thread(send_low_stock_alert, cid_str)
    )


    # 9) Build and return response
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
