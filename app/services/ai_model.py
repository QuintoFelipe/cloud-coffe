import asyncio
from vertexai.preview.generative_models import GenerativeModel
from app.config import settings
from vertexai import init
import os

_model = None

def get_gemini_model():
    global _model
    if _model is None:
        init(
            project=os.getenv("GCP_PROJECT"),  # Add this to your secrets
            location="us-central1"
        )
        _model = GenerativeModel("gemini-1.5-flash")
    return _model

async def classify_intent(text: str) -> str:
    prompt = (
        "Classify the user intent into one of: ORDER, INVENTORY, OTHER.\n"
        f"User: {text}\nIntent:"
    )
    response = get_gemini_model().generate_content(prompt)
    return response.text.strip().upper()
