import requests
from app.config import settings

def get_medellin_weather() -> str:
    """
    Returns a short description of current weather in Medellín, e.g. "Clear, 24°C".
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": "Medellin,CO",
        "appid": settings.OWM_API_KEY,
        "units": "metric",        # Celsius
        "lang": "en"
    }
    r = requests.get(url, params=params, timeout=5)
    r.raise_for_status()
    data = r.json()
    desc = data["weather"][0]["description"].capitalize()
    temp = round(data["main"]["temp"])
    return f"{desc}, {temp}°C"
