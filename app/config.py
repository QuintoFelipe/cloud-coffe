from pydantic import BaseSettings

class Settings(BaseSettings):
    GCP_PROJECT: str
    TELEGRAM_TOKEN: str
    GOOGLE_SHEET_ID: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    GEMINI_API_KEY: str

    class Config:
        case_sensitive = True

settings = Settings()
