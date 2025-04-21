import asyncio
from app.services.sheets import get_products

async def products_agent() -> str:
    products = await asyncio.to_thread(get_products)
    lines = [f"{p['product']}: ${p['price_unit_dolars']}" for p in products]
    return "Available products:\n" + "\n".join(lines)
