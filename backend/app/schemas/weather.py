from typing import Optional

from pydantic import BaseModel


class WeatherResponse(BaseModel):
    temperature: float
    feels_like: float
    temp_min: float
    temp_max: float
    humidity: int
    description: str
    condition: str
    icon: str
    wind_speed: float
    city: str
    country: str


class ForecastItem(BaseModel):
    datetime: str
    temperature: float
    feels_like: float
    temp_min: float
    temp_max: float
    description: str
    condition: str
    icon: str
    humidity: int
    wind_speed: float


class ForecastResponse(BaseModel):
    city: str
    country: str
    forecasts: list[ForecastItem]


class WeatherErrorResponse(BaseModel):
    error: str
