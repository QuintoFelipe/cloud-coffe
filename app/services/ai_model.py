from vertexai.preview.generative_models import GenerativeModel
from vertexai import init
from app.config import settings

_model = None

def get_gemini_model():
    global _model
    if _model is None:
        init(
            project=settings.GCP_PROJECT,
            location="us-central1"
        )
        _model = GenerativeModel("gemini-1.5-flash")
    return _model

async def classify_intent(text: str) -> str:
    prompt = (
        "Classify the user intent into one of: ORDER, INVENTORY, OTHER.\n"
        f"User: {text}\nIntent:"
    )
    response = await get_gemini_model().generate_content_async(prompt)
    return response.text.strip().upper()
