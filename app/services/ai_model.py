import asyncio
from google.cloud import aiplatform
from app.config import settings

_model = None

def get_gemini_model():
    global _model
    if _model is None:
        aiplatform.init()
        _model = aiplatform.TextGenerationModel.from_pretrained("gemini-2.0-flash")
    return _model

async def classify_intent(text: str) -> str:
    prompt = (
        "Classify the user intent into one of: ORDER, INVENTORY, OTHER.\n"
        f"User: {text}\nIntent:"
    )
    resp = get_gemini_model().predict(prompt=prompt, max_output_tokens=10)
    return resp.text.strip().upper()