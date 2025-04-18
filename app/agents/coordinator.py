from app.services.ai_model import classify_intent
from app.agents.order import order_agent
from app.agents.inventory import inventory_agent

async def coordinator_agent(text: str) -> str:
    intent = await classify_intent(text)
    if intent == "ORDER":
        return await order_agent(text)
    if intent == "INVENTORY":
        return await inventory_agent(text)
    return "Sorry, I can only help with orders or inventory."