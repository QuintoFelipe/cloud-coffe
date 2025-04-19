import gspread
from google.oauth2.service_account import Credentials
from app.config import settings
from google.auth import default  # ✅ use default GCP credentials

def get_sheets_client():
    creds, _ = default(scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(creds)


def get_inventory() -> list[dict]:
    client = get_sheets_client()
    sheet = client.open_by_key(settings.GOOGLE_SHEET_ID)
    return sheet.worksheet("Inventory").get_all_records()


def get_recipes() -> list[dict]:
    client = get_sheets_client()
    sheet = client.open_by_key(settings.GOOGLE_SHEET_ID)
    return sheet.worksheet("Recipes").get_all_records()


def add_order(order_id: str, product: str, timestamp: str):
    client = get_sheets_client()
    ws = client.open_by_key(settings.GOOGLE_SHEET_ID).worksheet("Orders")
    ws.append_row([order_id, product, timestamp])


def update_inventory(item: str, new_quantity: float):
    if new_quantity < 0:
        raise ValueError("new_quantity must be non-negative")
    client = get_sheets_client()
    ws = client.open_by_key(settings.GOOGLE_SHEET_ID).worksheet("Inventory")
    cell = ws.find(item)
    ws.update_cell(cell.row, 2, new_quantity)