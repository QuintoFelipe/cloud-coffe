import logging
import requests, threading
from app.config import settings
from app.services.sheets import get_inventory

log = logging.getLogger(__name__)


_last_alert_by_chat: dict[int, str] = {}
_lock = threading.Lock()  

def send_low_stock_alert(chat_id: int):
    """
    If any item is <= its minimum level, send ONE alert message into
    `chat_id`.  Suppress duplicates of the exact same alert text.
    """
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
        if _last_alert_by_chat.get(chat_id) == text:  
            log.info("duplicate low-stock alert suppressed")          
            return                                                    
        _last_alert_by_chat[chat_id] = text      



    # Dedup: if we already sent this exact text to this chat, skip
    if _last_alert_by_chat.get(chat_id) == text:
        log.info("send_low_stock_alert: duplicate alert suppressed")
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=5)
        if resp.status_code == 200:
            _last_alert_by_chat[chat_id] = text          # remember what we sent
            log.info("send_low_stock_alert: alert sent")
        else:
            log.error(f"Telegram API error {resp.status_code}: {resp.text}")
    except Exception as e:
        log.error(f"HTTP request failed while sending alert: {e}")
