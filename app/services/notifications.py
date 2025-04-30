import logging
import requests
from app.config import settings
from app.services.sheets import get_inventory

log = logging.getLogger(__name__)

def send_low_stock_alert(chat_id: int):
    """
    Check inventory; if any item.quantity <= minimum_level,
    send an alert into the given chat_id via a blocking HTTP request.
    """
    log.info(f"send_low_stock_alert: called for chat_id={chat_id}")
    inv = get_inventory()
    low = [
        r for r in inv
        if r.get("minimum_level") is not None
        and r["quantity"] <= r["minimum_level"]
    ]
    if not low:
        log.info("send_low_stock_alert: no items below minimum, exiting")
        return

    lines = [
        f"⚠️ Low stock: {r['item']} {r['quantity']}{r.get('unit','')} "
        f"(min {r['minimum_level']}{r.get('unit','')})"
        for r in low
    ]
    text = "\n".join(lines)

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    try:
        resp = requests.post(url, data=payload, timeout=5)
        if resp.status_code != 200:
            log.error(
                f"send_low_stock_alert: Telegram API returned {resp.status_code}: {resp.text}"
            )
        else:
            log.info("send_low_stock_alert: message sent via HTTP")
    except Exception as e:
        log.error(f"send_low_stock_alert: HTTP request failed: {e}")
