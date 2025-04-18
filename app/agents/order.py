import random
import asyncio
from datetime import datetime
from app.utils.fuzzy_match import exact_item_match
from app.services.sheets import get_recipes, get_inventory, update_inventory, add_order

async def order_agent(text: str) -> str:
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

    inv = await asyncio.to_thread(get_inventory)
    inv_map = {i['item'].lower(): i['quantity'] for i in inv}
    reqs = [r for r in recipes if r['item'].lower() == product]

    for r in reqs:
        ing = r['ingredient'].lower()
        needed = r['quantity_per_unit']
        if inv_map.get(ing, 0) < needed:
            return f"Sorry, not enough {ing}."

    def perform_order_tasks():
        for r in reqs:
            ing = r['ingredient'].lower()
            new_qty = inv_map[ing] - r['quantity_per_unit']
            update_inventory(r['ingredient'], new_qty)
        order_id = f"#{random.randint(1000,9999)}"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        add_order(order_id, product, timestamp)
        return order_id

    order_id = await asyncio.to_thread(perform_order_tasks)
    return f"Order {order_id} for {product} placed successfully."