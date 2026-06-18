import os
from typing import Optional

import httpx

YANDEX_WEATHER_API_KEY = os.getenv("YANDEX_WEATHER_API_KEY")
YANDEX_WEATHER_BASE_URL = "https://api.weather.yandex.ru/v2"


async def get_current_weather(lat: float, lon: float, lang: str = "ru_RU"):
    """
    Get current weather by coordinates using Yandex Weather API.

    Args:
        lat: Latitude (e.g., 55.7558 for Moscow)
        lon: Longitude (e.g., 37.6173 for Moscow)
        lang: Language (ru_RU, en_US, tr_TR)

    Returns:
        dict: Weather data including temperature, conditions, etc.
    """
    if not YANDEX_WEATHER_API_KEY:
        return {"error": "Weather API key not configured"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{YANDEX_WEATHER_BASE_URL}/informers",
                params={"lat": lat, "lon": lon, "lang": lang},
                headers={"X-Yandex-API-Key": YANDEX_WEATHER_API_KEY},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            fact = data["fact"]
            return {
                "temperature": fact["temp"],
                "feels_like": fact["feels_like"],
                "condition": fact["condition"],
                "wind_speed": fact["wind_speed"],
                "wind_dir": fact.get("wind_dir", ""),
                "pressure_mm": fact["pressure_mm"],
                "humidity": fact["humidity"],
                "daytime": fact["daytime"],
                "season": fact["season"],
                "icon": fact["icon"],
                "obs_time": fact["obs_time"],
                "location": data.get("geo_object", {}).get("locality", {}).get("name", ""),
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                return {"error": "Invalid API key"}
            return {"error": f"Weather API error: {e.response.status_code}"}
        except httpx.TimeoutException:
            return {"error": "Weather API timeout"}
        except Exception as e:
            return {"error": f"Failed to fetch weather: {str(e)}"}


async def get_weather_forecast(lat: float, lon: float, lang: str = "ru_RU", limit: int = 7):
    """
    Get weather forecast using Yandex Weather API.

    Args:
        lat: Latitude
        lon: Longitude
        lang: Language (ru_RU, en_US, tr_TR)
        limit: Number of forecast days (max 7)

    Returns:
        dict: Forecast data
    """
    if not YANDEX_WEATHER_API_KEY:
        return {"error": "Weather API key not configured"}

    if limit > 7:
        limit = 7  # Yandex max

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{YANDEX_WEATHER_BASE_URL}/forecast",
                params={"lat": lat, "lon": lon, "lang": lang, "limit": limit, "hours": True},
                headers={"X-Yandex-API-Key": YANDEX_WEATHER_API_KEY},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            forecasts = []
            for day in data.get("forecasts", []):
                day_info = day["parts"]["day"]
                forecasts.append(
                    {
                        "date": day["date"],
                        "temp_avg": day_info["temp_avg"],
                        "temp_min": day_info.get("temp_min", day_info["temp_avg"]),
                        "temp_max": day_info.get("temp_max", day_info["temp_avg"]),
                        "feels_like": day_info["feels_like"],
                        "condition": day_info["condition"],
                        "humidity": day_info["humidity"],
                        "wind_speed": day_info["wind_speed"],
                        "pressure_mm": day_info["pressure_mm"],
                        "icon": day_info["icon"],
                        "daytime": day_info["daytime"],
                    }
                )

            return {
                "location": data.get("geo_object", {}).get("locality", {}).get("name", ""),
                "forecasts": forecasts,
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                return {"error": "Invalid API key"}
            return {"error": f"Weather API error: {e.response.status_code}"}
        except httpx.TimeoutException:
            return {"error": "Weather API timeout"}
        except Exception as e:
            return {"error": f"Failed to fetch forecast: {str(e)}"}


# City coordinates for common Russian cities (helper)
CITY_COORDINATES = {
    "москва": {"lat": 55.7558, "lon": 37.6173, "name": "Москва"},
    "moscow": {"lat": 55.7558, "lon": 37.6173, "name": "Москва"},
    "санкт-петербург": {"lat": 59.9311, "lon": 30.3609, "name": "Санкт-Петербург"},
    "saint petersburg": {"lat": 59.9311, "lon": 30.3609, "name": "Санкт-Петербург"},
    "новосибирск": {"lat": 55.0084, "lon": 82.9357, "name": "Новосибирск"},
    "novosibirsk": {"lat": 55.0084, "lon": 82.9357, "name": "Новосибирск"},
    "екатеринбург": {"lat": 56.8389, "lon": 60.6057, "name": "Екатеринбург"},
    "yekaterinburg": {"lat": 56.8389, "lon": 60.6057, "name": "Екатеринбург"},
    "казань": {"lat": 55.8304, "lon": 49.0661, "name": "Казань"},
    "kazan": {"lat": 55.8304, "lon": 49.0661, "name": "Казань"},
    "нижний новгород": {"lat": 56.2965, "lon": 43.9361, "name": "Нижний Новгород"},
    "nizhniy novgorod": {"lat": 56.2965, "lon": 43.9361, "name": "Нижний Новгород"},
    "челябинск": {"lat": 55.1644, "lon": 61.4368, "name": "Челябинск"},
    "chelyabinsk": {"lat": 55.1644, "lon": 61.4368, "name": "Челябинск"},
    "самара": {"lat": 53.2001, "lon": 50.1500, "name": "Самара"},
    "samara": {"lat": 53.2001, "lon": 50.1500, "name": "Самара"},
    "омск": {"lat": 54.9885, "lon": 73.3242, "name": "Омск"},
    "omsk": {"lat": 54.9885, "lon": 73.3242, "name": "Омск"},
    "ростов-на-дону": {"lat": 47.2357, "lon": 39.7015, "name": "Ростов-на-Дону"},
    "rostov-on-don": {"lat": 47.2357, "lon": 39.7015, "name": "Ростов-на-Дону"},
    "уфа": {"lat": 54.7388, "lon": 55.9721, "name": "Уфа"},
    "ufa": {"lat": 54.7388, "lon": 55.9721, "name": "Уфа"},
    "красноярск": {"lat": 56.0153, "lon": 92.8932, "name": "Красноярск"},
    "krasnoyarsk": {"lat": 56.0153, "lon": 92.8932, "name": "Красноярск"},
    "воронеж": {"lat": 51.6720, "lon": 39.1843, "name": "Воронеж"},
    "voronezh": {"lat": 51.6720, "lon": 39.1843, "name": "Воронеж"},
    "пермь": {"lat": 58.0105, "lon": 56.2502, "name": "Пермь"},
    "perm": {"lat": 58.0105, "lon": 56.2502, "name": "Пермь"},
    "волгоград": {"lat": 48.7080, "lon": 44.5133, "name": "Волгоград"},
    "volgograd": {"lat": 48.7080, "lon": 44.5133, "name": "Волгоград"},
}


def get_city_coordinates(city_name: str) -> Optional[dict]:
    """Get coordinates for a known city (supports Russian and English names)."""
    city_key = city_name.lower().strip()
    return CITY_COORDINATES.get(city_key)
