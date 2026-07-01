from pydantic import BaseModel, Field


class LocationUpdate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class LocationResponse(BaseModel):
    latitude: float | None = None
    longitude: float | None = None


class WeatherResponse(BaseModel):
    temperature: float
    feels_like: float
    humidity: int
    weather_code: int
    weather_description: str
    wind_speed: float
    timestamp: str
    latitude: float
    longitude: float
    temperature_unit: str = "°C"
    city_name: str = ""
