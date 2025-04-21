from vertexai.preview.generative_models import GenerativeModel
from app.config import settings
from vertexai import init
import logging

logger = logging.getLogger(__name__)
_model = None

def get_gemini_model() -> GenerativeModel:
    global _model
    if _model is None:
        init(project=settings.GCP_PROJECT, location="us-central1")
        _model = GenerativeModel("gemini-1.5-flash")
    return _model

async def classify_intent(text: str) -> str:
    prompt = (
        "You are an intent classifier for a global, multi‑language coffee assistant.\n"
        "Your job is to read the user's message (which may be in English, Spanish, French, etc.)\n"
        "and map it to exactly one of these intents, based on what this assistant can do:\n"
        "  • ORDER: the user wants to place an order or ask about ordering a drink.\n"
        "  • INVENTORY: the user wants inventory levels or stock status.\n"
        "  • PRODUCTS: the user wants to see the list of available products and their prices.\n"
        "  • OTHER: anything else (small talk, off‑topic, help, etc.).\n"
        "Return only the intent token (ORDER, INVENTORY, PRODUCTS or OTHER), in ALL CAPS.\n"
        f"User message: \"{text}\"\n"
        "Intent:"
    )
    try:
        logger.info(f"[Gemini Request] {prompt}")
        resp = await get_gemini_model().generate_content_async(prompt)
        intent = resp.text.strip().upper()
        return intent if intent in {"ORDER", "INVENTORY", "PRODUCTS", "OTHER"} else "OTHER"
    except Exception as e:
        logger.error(f"[Gemini ERROR]: {e}")
        return "OTHER"
