import logging
from dataclasses import dataclass
from typing import Optional

import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 10.0

WMO_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

logger = logging.getLogger(__name__)


@dataclass
class WeatherData:
    temperature: float
    feels_like: float
    humidity: int
    weather_code: int
    weather_description: str
    wind_speed: float
    timestamp: str
    latitude: float
    longitude: float


def _describe_weather(code: int) -> str:
    return WMO_CODES.get(code, "Unknown")


async def get_city_name(latitude: float, longitude: float) -> str:
    """Reverse geocode coordinates to a city name via Nominatim."""
    headers = {
        "User-Agent": "DigitalWardrobe/1.0 (wardrobe-app)",
        "Accept-Language": "ru,en",
    }
    params = {
        "lat": latitude,
        "lon": longitude,
        "format": "json",
        "zoom": 10,
    }
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            resp = await client.get(NOMINATIM_URL, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            logger.warning("Nominatim reverse geocode failed for %s, %s", latitude, longitude)
            return ""

    address = data.get("address", {})
    return address.get("city") or address.get("town") or address.get("village") or address.get("state", "")


async def fetch_weather(latitude: float, longitude: float) -> Optional[WeatherData]:
    """Fetch current weather from Open-Meteo API for the given coordinates.

    Returns ``None`` when the API call fails or returns invalid data.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "timezone": "auto",
    }

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = await client.get(OPEN_METEO_URL, params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Open-Meteo returned error: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Open-Meteo request failed: {e}")
            return None
        except ValueError as e:
            logger.error(f"Failed to parse Open-Meteo response: {e}")
            return None

    current = data.get("current")
    if not current:
        logger.error("Open-Meteo response missing 'current' field")
        return None

    weather_code = current.get("weather_code", 0)

    return WeatherData(
        temperature=current.get("temperature_2m", 0.0),
        feels_like=current.get("apparent_temperature", 0.0),
        humidity=current.get("relative_humidity_2m", 0),
        weather_code=weather_code,
        weather_description=_describe_weather(weather_code),
        wind_speed=current.get("wind_speed_10m", 0.0),
        timestamp=current.get("time", ""),
        latitude=latitude,
        longitude=longitude,
    )
