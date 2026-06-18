from typing import Optional, Union

from fastapi import APIRouter, Query

from app.schemas.weather import ForecastResponse, WeatherErrorResponse, WeatherResponse
from app.services.weather import get_city_coordinates, get_current_weather, get_weather_forecast

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/current", response_model=Union[WeatherResponse, WeatherErrorResponse])
async def get_weather(
    lat: Optional[float] = Query(None, description="Latitude (e.g., 55.7558 for Moscow)"),
    lon: Optional[float] = Query(None, description="Longitude (e.g., 37.6173 for Moscow)"),
    city: Optional[str] = Query(None, description="City name in Russian or English (e.g., 'Москва', 'Moscow')"),
    lang: str = Query("ru_RU", description="Language: ru_RU (Russian), en_US (English), tr_TR (Turkish)"),
):
    """
    Get current weather using Yandex Weather API.

    Provide either:
    - lat & lon coordinates, OR
    - city name (for common Russian cities)

    Free tier: 25,000 calls/day - Perfect for Russian users!
    """
    # If city provided, get coordinates
    if city and not (lat and lon):
        coords = get_city_coordinates(city)
        if not coords:
            return {"error": f"City '{city}' not found. Use lat/lon coordinates or choose from major Russian cities."}
        lat = coords["lat"]
        lon = coords["lon"]

    if not lat or not lon:
        return {"error": "Provide either lat/lon coordinates or a city name"}

    weather_data = await get_current_weather(lat, lon, lang)
    return weather_data


@router.get("/forecast", response_model=Union[ForecastResponse, WeatherErrorResponse])
async def get_forecast(
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    city: Optional[str] = Query(None, description="City name in Russian or English"),
    lang: str = Query("ru_RU", description="Language: ru_RU, en_US, tr_TR"),
    days: int = Query(7, ge=1, le=7, description="Number of forecast days (1-7)"),
):
    """
    Get weather forecast for next 1-7 days using Yandex Weather API.

    Provide either lat/lon or city name for common Russian cities.
    """
    # If city provided, get coordinates
    if city and not (lat and lon):
        coords = get_city_coordinates(city)
        if not coords:
            return {"error": f"City '{city}' not found. Use lat/lon coordinates."}
        lat = coords["lat"]
        lon = coords["lon"]

    if not lat or not lon:
        return {"error": "Provide either lat/lon coordinates or a city name"}

    forecast_data = await get_weather_forecast(lat, lon, lang, days)
    return forecast_data


@router.get("/cities")
def get_available_cities():
    """
    Get list of Russian cities with pre-configured coordinates.

    For other cities, use lat/lon coordinates from Telegram WebApp or GPS.
    """
    from app.services.weather import CITY_COORDINATES

    cities = []
    seen = set()
    for key, value in CITY_COORDINATES.items():
        if value["name"] not in seen:
            cities.append(
                {"name": value["name"], "name_en": key if key.isascii() else "", "lat": value["lat"], "lon": value["lon"]}
            )
            seen.add(value["name"])

    return {"cities": cities}
