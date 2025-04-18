from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from telegram.ext import Application
from app.agents.coordinator import coordinator_agent
from app.bot.telegram import get_bot_app

router = APIRouter()

class TelegramUpdate(BaseModel):
    update_id: int
    message: dict

@router.post("/webhook")
async def webhook(
    update: TelegramUpdate,
    app: Application = Depends(get_bot_app)
):
    chat = update.message.get("chat", {})
    chat_id = chat.get("id")
    text = update.message.get("text")
    if not chat_id or not text:
        return {"status": "ignored"}
    try:
        response = await coordinator_agent(text)
        await app.bot.send_message(chat_id, response)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))