import logging, requests, threading
from app.config import settings
from app.services.sheets import get_inventory

log   = logging.getLogger(__name__)
_lock = threading.Lock()
_last_alert_by_chat: dict[int, str] = {}

def send_low_stock_alert(chat_id: int):
    """Send ONE low-stock alert into chat_id; suppress duplicates."""
    inv  = get_inventory()
    low  = [
        r for r in inv
        if r.get("minimum_level") is not None
        and r["quantity"] <= r["minimum_level"]
    ]
    if not low:
        return

    text = "\n".join(
        f"⚠️ Low stock: {r['item']} {r['quantity']}{r.get('unit','')} "
        f"(min {r['minimum_level']}{r.get('unit','')})"
        for r in low
    )

    with _lock:
        if _last_alert_by_chat.get(chat_id) == text:
            log.info("duplicate low-stock alert suppressed")
            return

    # ─── send the message ─────────────────────────────────────────
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=5)
        if r.status_code == 200:
            log.info("low-stock alert sent")
            with _lock:                       # cache ONLY after success
                _last_alert_by_chat[chat_id] = text
        else:
            log.error(f"Telegram error {r.status_code}: {r.text}")
    except Exception as e:
        log.error(f"HTTP request failed while sending alert: {e}")
