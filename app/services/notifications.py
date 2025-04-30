from telegram import Bot
from app.config import settings
from app.services.sheets import get_inventory
import logging

log = logging.getLogger(__name__)

def send_low_stock_alert(chat_id: str):
    """
    Check inventory; if any item.quantity <= minimum_level,
    send an alert into the given chat_id.
    """
    inv = get_inventory()
    low = [
        r for r in inv
        if r.get("minimum_level") is not None and r["quantity"] <= r["minimum_level"]
    ]
    if not low:
        return

    lines = [
        f"⚠️ Low stock: {r['item']} {r['quantity']}{r.get('unit','')} "
        f"(min {r['minimum_level']}{r.get('unit','')})"
        for r in low
    ]
    text = "\n".join(lines)
    try:
        Bot(token=settings.TELEGRAM_TOKEN).send_message(chat_id=chat_id, text=text)
    except Exception as e:
        log.error(f"Failed to send low-stock alert to {chat_id}: {e}")
