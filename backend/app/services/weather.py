import os
from typing import Optional

import httpx

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"


async def get_current_weather(city: str, country_code: Optional[str] = None):
    """
    Get current weather for a city.

    Args:
        city: City name (e.g., "Tashkent", "New York")
        country_code: Optional ISO 3166 country code (e.g., "UZ", "US")

    Returns:
        dict: Weather data including temperature, conditions, etc.
    """
    if not OPENWEATHER_API_KEY:
        return {"error": "Weather API key not configured"}

    location = f"{city},{country_code}" if country_code else city

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{OPENWEATHER_BASE_URL}/weather",
                params={
                    "q": location,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric",  # Celsius
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "temp_min": data["main"]["temp_min"],
                "temp_max": data["main"]["temp_max"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "condition": data["weather"][0]["main"],
                "icon": data["weather"][0]["icon"],
                "wind_speed": data["wind"]["speed"],
                "city": data["name"],
                "country": data["sys"]["country"],
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": "City not found"}
            return {"error": f"Weather API error: {e.response.status_code}"}
        except httpx.TimeoutException:
            return {"error": "Weather API timeout"}
        except Exception as e:
            return {"error": f"Failed to fetch weather: {str(e)}"}


async def get_weather_forecast(city: str, country_code: Optional[str] = None, days: int = 5):
    """
    Get weather forecast for next N days.

    Args:
        city: City name
        country_code: Optional ISO 3166 country code
        days: Number of days (1-5 for free tier)

    Returns:
        dict: Forecast data
    """
    if not OPENWEATHER_API_KEY:
        return {"error": "Weather API key not configured"}

    if days > 5:
        days = 5  # Free tier limit

    location = f"{city},{country_code}" if country_code else city

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{OPENWEATHER_BASE_URL}/forecast",
                params={
                    "q": location,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric",
                    "cnt": days * 8,  # 8 forecasts per day (3-hour intervals)
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Group by day
            forecasts = []
            for item in data["list"]:
                forecasts.append(
                    {
                        "datetime": item["dt_txt"],
                        "temperature": item["main"]["temp"],
                        "feels_like": item["main"]["feels_like"],
                        "temp_min": item["main"]["temp_min"],
                        "temp_max": item["main"]["temp_max"],
                        "description": item["weather"][0]["description"],
                        "condition": item["weather"][0]["main"],
                        "icon": item["weather"][0]["icon"],
                        "humidity": item["main"]["humidity"],
                        "wind_speed": item["wind"]["speed"],
                    }
                )

            return {"city": data["city"]["name"], "country": data["city"]["country"], "forecasts": forecasts}

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": "City not found"}
            return {"error": f"Weather API error: {e.response.status_code}"}
        except httpx.TimeoutException:
            return {"error": "Weather API timeout"}
        except Exception as e:
            return {"error": f"Failed to fetch forecast: {str(e)}"}
