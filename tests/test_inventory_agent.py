import pytest
from app.agents.inventory import inventory_agent

@pytest.mark.asyncio
async def test_inventory_specific(monkeypatch):
    inventory = [{'item':'milk','quantity':5,'unit':'L','minimum_level':2}]
    monkeypatch.setattr('app.services.sheets.get_inventory', lambda: inventory)
    res = await inventory_agent("milk")
    assert "milk: 5L (min 2L)" in res

@pytest.mark.asyncio
async def test_inventory_low(monkeypatch):
    inventory = [
        {'item':'milk','quantity':1,'unit':'L','minimum_level':2},
        {'item':'coffee','quantity':3,'unit':'kg','minimum_level':1}
    ]
    monkeypatch.setattr('app.services.sheets.get_inventory', lambda: inventory)
    res = await inventory_agent("status")
    assert "Items below minimum:" in res