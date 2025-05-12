import logging, requests, threading
from app.config import settings
from app.services.sheets import get_inventory
# import the normalizer you wrote in inventory.py
from app.agents.inventory import normalize_inventory  

log   = logging.getLogger(__name__)
_lock = threading.Lock()
_last_alert_by_chat: dict[str, str] = {}

def send_low_stock_alert(chat_id: int | str):
    chat_key = str(chat_id)

    # 1) Load raw inventory
    raw = get_inventory()
    log.info(f"send_low_stock_alert: RAW inventory rows: {raw!r}")

    # 2) Normalize
    inv = normalize_inventory(raw)

    # 3) Filter true low-stock items
    low = [r for r in inv if r['quantity'] <= r['minimum_level']]
    if not low:
        log.info("send_low_stock_alert: nothing below minimum, skipping alert")
        return

    # 4) Build the single alert text
    text = "\n".join(
        f"⚠️ Low stock: {r['item']} {r['quantity']}{r['unit']} "
        f"(min {r['minimum_level']}{r['unit']})"
        for r in low
    )

    # 5) Dedupe & reserve
    with _lock:
        if _last_alert_by_chat.get(chat_key) == text:
            log.info("send_low_stock_alert: duplicate alert suppressed")
            return
        _last_alert_by_chat[chat_key] = text

    # 6) Send via HTTP
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, data={"chat_id": chat_key, "text": text}, timeout=5)
        if resp.status_code == 200:
            log.info("send_low_stock_alert: alert successfully sent")
        else:
            log.error(f"Telegram error {resp.status_code}: {resp.text}")
            with _lock:
                _last_alert_by_chat.pop(chat_key, None)
    except Exception as e:
        log.error(f"HTTP request failed: {e}")
        with _lock:
            _last_alert_by_chat.pop(chat_key, None)
