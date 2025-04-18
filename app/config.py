from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    GOOGLE_SHEET_ID: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()