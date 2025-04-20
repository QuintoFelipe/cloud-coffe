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
        "You are an intent classifier for a coffee assistant.\n"
        "Return only one of: ORDER, INVENTORY, OTHER.\n"
        f"User message: {text}\nIntent:"
    )
    try:
        logger.info(f"[Gemini Request] {prompt}")
        resp = await get_gemini_model().generate_content_async(prompt)
        intent = resp.text.strip().upper()
        return intent if intent in {"ORDER", "INVENTORY", "OTHER"} else "OTHER"
    except Exception as e:
        logger.error(f"[Gemini ERROR]: {e}")
        return "OTHER"
