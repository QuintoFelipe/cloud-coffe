from pydantic import BaseSettings

class Settings(BaseSettings):
    # GCP project (for Vertex AI)
    GCP_PROJECT: str

    # Telegram
    TELEGRAM_TOKEN: str

    # Google Sheets
    GOOGLE_SHEET_ID: str

    # path to your JSON key when running locally.
    # Cloud Run will _not_ set this, so it falls back to None.
    GOOGLE_APPLICATION_CREDENTIALS: str = None

    # Gemini API (if you need it locally)
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
