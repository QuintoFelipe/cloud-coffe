from app.services.ai_model import classify_intent
from app.agents.order import order_agent
from app.agents.inventory import inventory_agent
from app.agents.products import products_agent
import logging

logger = logging.getLogger(__name__)

async def coordinator_agent(text: str, chat_id: str) -> str:
    """
    Routes user messages to the right agent based on Gemini intent:
      • ORDER     → order_agent
      • INVENTORY → inventory_agent
      • PRODUCTS  → products_agent
      • OTHER     → fallback
    """
    # 1) Ask Gemini to classify
    intent = await classify_intent(text)
    logger.info(f"[Coordinator] Intent detected: {intent}")

    # 2) Dispatch to the right agent
    if intent == "ORDER":
        return await order_agent(text, chat_id)
    if intent == "INVENTORY":
        return await inventory_agent(text)
    if intent == "PRODUCTS":
        return await products_agent()
    
    return (      
        "Lo siento, solo puedo ayudar con pedidos, inventario o listar productos.\n"
        "I'm sorry, I can only help with orders, inventory, or product listings.")
