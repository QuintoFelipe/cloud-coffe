from pydantic import BaseSettings

class Settings(BaseSettings):
    GCP_PROJECT: str
    TELEGRAM_TOKEN: str
    GOOGLE_SHEET_ID: str
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
