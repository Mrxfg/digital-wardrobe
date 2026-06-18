from typing import Optional, Union

from fastapi import APIRouter, Query

from app.schemas.weather import ForecastResponse, WeatherErrorResponse, WeatherResponse
from app.services.weather import get_current_weather, get_weather_forecast

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/current", response_model=Union[WeatherResponse, WeatherErrorResponse])
async def get_weather(
    city: str = Query(..., description="City name (e.g., 'Tashkent', 'New York')"),
    country: Optional[str] = Query(None, description="ISO 3166 country code (e.g., 'UZ', 'US')"),
):
    """
    Get current weather for a city.

    Free tier: 1000 calls/day from OpenWeatherMap.
    Perfect for ~1000 users checking weather once per day.
    """
    weather_data = await get_current_weather(city, country)
    return weather_data


@router.get("/forecast", response_model=Union[ForecastResponse, WeatherErrorResponse])
async def get_forecast(
    city: str = Query(..., description="City name"),
    country: Optional[str] = Query(None, description="ISO 3166 country code"),
    days: int = Query(3, ge=1, le=5, description="Number of forecast days (1-5)"),
):
    """
    Get weather forecast for next 1-5 days.

    Returns 3-hour interval forecasts.
    Free tier supports up to 5 days.
    """
    forecast_data = await get_weather_forecast(city, country, days)
    return forecast_data
