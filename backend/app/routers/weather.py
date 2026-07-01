from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.users import User
from app.schemas.weather import LocationUpdate, LocationResponse, WeatherResponse
from app.services.weather import fetch_weather, get_city_name

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/", response_model=WeatherResponse)
async def get_weather(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetch current weather for the user's saved location.

    Returns 200 with weather data when coordinates are saved.
    Returns 404 when no location is set.
    """
    user = db.query(User).filter(User.id == current_user["user_id"]).first()

    if not user or user.latitude is None or user.longitude is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not set. Please save your location first.",
        )

    weather = await fetch_weather(user.latitude, user.longitude)

    if weather is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch weather data from external service.",
        )

    city_name = await get_city_name(user.latitude, user.longitude)

    return WeatherResponse(
        temperature=weather.temperature,
        feels_like=weather.feels_like,
        humidity=weather.humidity,
        weather_code=weather.weather_code,
        weather_description=weather.weather_description,
        wind_speed=weather.wind_speed,
        timestamp=weather.timestamp,
        latitude=weather.latitude,
        longitude=weather.longitude,
        city_name=city_name,
    )


@router.get("/location", response_model=LocationResponse)
def get_location(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Return the user's saved location coordinates.

    Returns 200 with coordinates when set, or null fields when not set.
    """
    user = db.query(User).filter(User.id == current_user["user_id"]).first()

    if not user:
        return LocationResponse(latitude=None, longitude=None)

    return LocationResponse(latitude=user.latitude, longitude=user.longitude)


@router.post("/location", response_model=LocationResponse, status_code=status.HTTP_200_OK)
def save_location(
    location: LocationUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save or update the user's location coordinates.

    Expects ``{"latitude": 59.93, "longitude": 30.36}``.
    Latitude must be in [-90, 90], longitude in [-180, 180].
    """
    user = db.query(User).filter(User.id == current_user["user_id"]).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.latitude = location.latitude
    user.longitude = location.longitude
    db.commit()
    db.refresh(user)

    return LocationResponse(latitude=user.latitude, longitude=user.longitude)
