from vertexai.preview.generative_models import GenerativeModel
from app.config import settings
from vertexai import init
import os

_model = None

def get_gemini_model() -> GenerativeModel:
    global _model
    if _model is None:
        # Init Vertex AI solo una vez, en lazy-load
        init(
            project=settings.GCP_PROJECT,  # Ya lo sacas de Pydantic
            location="us-central1"
        )
        _model = GenerativeModel("gemini-1.5-flash")
    return _model

import logging
logger = logging.getLogger(__name__)

async def classify_intent(text: str) -> str:
    prompt = (
        "Classify the user intent into one of: ORDER, INVENTORY, OTHER.\n"
        f"User: {text}\nIntent:"
    )
    model = get_gemini_model()
    try:
        logger.info(f"[Gemini Request] Prompt: {prompt}")
        response = await model.generate_content_async(prompt)
        intent = response.text.strip().upper()
        logger.info(f"[Gemini Response] Intent: {intent}")
        return intent if intent in {"ORDER", "INVENTORY", "OTHER"} else "OTHER"
    except Exception as e:
        logger.error(f"[Gemini ERROR]: {e}")
        return "OTHER"


