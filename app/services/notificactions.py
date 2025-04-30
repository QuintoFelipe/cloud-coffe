from telegram import Bot
from app.config import settings
from app.services.sheets import get_inventory

def send_low_stock_alert():
    """
    Check inventory; if any item.quantity <= item.minimum_level,
    send a single Telegram message listing them.
    """
    inv = get_inventory()
    low = [
        r for r in inv
        if r.get("minimum_level") is not None and r["quantity"] <= r["minimum_level"]
    ]
    if not low:
        return

    lines = [
        f"⚠️ Low stock alert: {r['item']}: {r['quantity']}{r.get('unit','')} "
        f"(min {r.get('minimum_level')}{r.get('unit','')})"
        for r in low
    ]
    text = "\n".join(lines)
    bot = Bot(token=settings.TELEGRAM_TOKEN)
    bot.send_message(chat_id=settings.ALERT_CHAT_ID, text=text)
