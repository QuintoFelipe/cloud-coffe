from telegram.ext import ApplicationBuilder
from app.config import settings

def get_bot_app() -> Application:
    return ApplicationBuilder() \
        .token(settings.TELEGRAM_TOKEN) \
        .build()