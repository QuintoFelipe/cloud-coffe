import random
import re
import asyncio
from datetime import datetime
from app.utils.fuzzy_match import exact_item_match
from app.services.sheets import get_recipes, get_inventory, update_inventory, add_order, get_products

async def order_agent(text: str) -> str:

    # 1) detect quantity (e.g. "2 lattes"); default to 1
    qty_match = re.search(r'\b(\d+)\b', text)
    quantity = int(qty_match.group(1)) if qty_match else 1

    # 2) detect product (e.g. "latte")
    recipes = await asyncio.to_thread(get_recipes)
    items = {r['item'].lower() for r in recipes}
    product = None
    for word in text.lower().split():
        match = exact_item_match(word, list(items))
        if match:
            product = match
            break
    if not product:
        return "Sorry, we don't have that product right now."
    
    # 3) check inventory for all ingredients needed × quantity
    inv = await asyncio.to_thread(get_inventory)
    inv_map = {i['item'].lower(): i['quantity'] for i in inv}
    reqs = [r for r in recipes if r['item'].lower() == product]

    for r in reqs:
        ing = r['ingredient'].lower()
        needed = r['quantity_per_unit'] * quantity
        if inv_map.get(ing, 0) < needed:
            return f"Sorry, not enough {ing}."

     # 4) lookup unit price and compute total
    products = await asyncio.to_thread(get_products)
    unit_price = next(
        (p['price_unit_dolars'] for p in products if p['product'].lower() == product),
        None
    )
    if unit_price is None:
        return "Sorry, couldn't find product price."
    total_price = unit_price * quantity


    def perform_order_tasks():
        for r in reqs:
            ing = r['ingredient'].lower()
            new_qty = inv_map[ing] - r['quantity_per_unit']
            update_inventory(r['ingredient'], new_qty)
        order_id = f"#{random.randint(1000,9999)}"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        add_order(order_id, product, timestamp,quantity, total_price)
        return order_id

    order_id = await asyncio.to_thread(perform_order_tasks)
    return (
        f"Order {order_id} for {quantity} × {product}(s) placed successfully. "
        f"Total price: ${total_price:.2f}"
            )