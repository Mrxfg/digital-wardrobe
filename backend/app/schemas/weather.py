from typing import Optional

from pydantic import BaseModel


class WeatherResponse(BaseModel):
    temperature: int
    feels_like: int
    condition: str
    wind_speed: float
    wind_dir: str
    pressure_mm: int
    humidity: int
    daytime: str
    season: str
    icon: str
    obs_time: int
    location: str


class ForecastItem(BaseModel):
    date: str
    temp_avg: int
    temp_min: int
    temp_max: int
    feels_like: int
    condition: str
    humidity: int
    wind_speed: float
    pressure_mm: int
    icon: str
    daytime: str


class ForecastResponse(BaseModel):
    location: str
    forecasts: list[ForecastItem]


class WeatherErrorResponse(BaseModel):
    error: str
