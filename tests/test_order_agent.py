<<<<<<< HEAD
import pytest
from app.agents.order import order_agent
from app.services.sheets import get_recipes, get_inventory

@pytest.mark.asyncio
async def test_order_success(monkeypatch):
    recipes = [{'item':'latte','ingredient':'milk','quantity_per_unit':1}]
    inventory = [{'item':'milk','quantity':10,'unit':'L','minimum_level':2}]
    monkeypatch.setattr('app.services.sheets.get_recipes', lambda: recipes)
    monkeypatch.setattr('app.services.sheets.get_inventory', lambda: inventory)
    res = await order_agent("Order latte")
    assert "Order" in res

@pytest.mark.asyncio
async def test_order_out_of_stock(monkeypatch):
    recipes = [{'item':'espresso','ingredient':'coffee','quantity_per_unit':2}]
    inventory = [{'item':'coffee','quantity':1,'unit':'kg','minimum_level':1}]
    monkeypatch.setattr('app.services.sheets.get_recipes', lambda: recipes)
    monkeypatch.setattr('app.services.sheets.get_inventory', lambda: inventory)
    res = await order_agent("Order espresso")
=======
import pytest
from app.agents.order import order_agent
from app.services.sheets import get_recipes, get_inventory

@pytest.mark.asyncio
async def test_order_success(monkeypatch):
    recipes = [{'item':'latte','ingredient':'milk','quantity_per_unit':1}]
    inventory = [{'item':'milk','quantity':10,'unit':'L','minimum_level':2}]
    monkeypatch.setattr('app.services.sheets.get_recipes', lambda: recipes)
    monkeypatch.setattr('app.services.sheets.get_inventory', lambda: inventory)
    res = await order_agent("Order latte")
    assert "Order" in res

@pytest.mark.asyncio
async def test_order_out_of_stock(monkeypatch):
    recipes = [{'item':'espresso','ingredient':'coffee','quantity_per_unit':2}]
    inventory = [{'item':'coffee','quantity':1,'unit':'kg','minimum_level':1}]
    monkeypatch.setattr('app.services.sheets.get_recipes', lambda: recipes)
    monkeypatch.setattr('app.services.sheets.get_inventory', lambda: inventory)
    res = await order_agent("Order espresso")
>>>>>>> bdfc648e5da2da83f3c00b80590671bad6c12a0e
    assert res == "Sorry, not enough coffee."