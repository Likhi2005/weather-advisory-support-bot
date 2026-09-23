from langchain_core.tools import tool

from services.weather_service import WeatherService


weather_service = WeatherService()


@tool
def weather_tool(latitude: float, longitude: float) -> dict:
    """Fetch current weather data from Open-Meteo
    for the given latitude and longitude."""
    try:
        return weather_service.get_weather(
            latitude=latitude,
            longitude=longitude
        )
    except Exception as e:
        return {"error": str(e)}