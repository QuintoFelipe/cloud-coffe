import logging, requests, threading
from app.config import settings
from app.services.sheets import get_inventory

log   = logging.getLogger(__name__)
_lock = threading.Lock()
_last_alert_by_chat: dict[str, str] = {}   # key is *string* chat_id

def send_low_stock_alert(chat_id: int | str):
    """Send ONE low-stock alert per chat; suppress exact duplicates."""
    chat_key = str(chat_id)                # ← normalise

    inv = get_inventory()
    low = [
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
        if _last_alert_by_chat.get(chat_key) == text:
            log.info("duplicate low-stock alert suppressed")
            return
        _last_alert_by_chat[chat_key] = text   # reserve before send

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, data={"chat_id": chat_key, "text": text}, timeout=5)
        if resp.status_code == 200:
            log.info("low-stock alert sent")
        else:
            log.error(f"Telegram error {resp.status_code}: {resp.text}")
            # roll back reservation on failure
            with _lock:
                _last_alert_by_chat.pop(chat_key, None)
    except Exception as e:
        log.error(f"HTTP request failed: {e}")
        with _lock:
            _last_alert_by_chat.pop(chat_key, None)
