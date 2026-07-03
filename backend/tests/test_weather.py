"""Unit and integration tests for Weather API.

Covers current weather retrieval, location save/retrieve, and
validation for coordinate ranges and types.
"""

from unittest.mock import patch

import pytest

from app.models.users import User
from app.services.weather import WeatherData

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

MOCK_WEATHER = WeatherData(
    temperature=20.5,
    feels_like=19.0,
    humidity=65,
    weather_code=2,
    weather_description="Partly cloudy",
    wind_speed=12.3,
    timestamp="2025-01-01T12:00",
    latitude=59.93,
    longitude=30.36,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_user(db_session, latitude=None, longitude=None):
    """Ensure a user with id=1 exists in the test database."""
    user = db_session.query(User).filter(User.id == 1).first()
    if not user:
        user = User(id=1, telegram_id="123456789", username="testuser")
        db_session.add(user)
    user.latitude = latitude
    user.longitude = longitude
    db_session.commit()


# ===================================================================
# GET /weather/
# ===================================================================


class TestGetWeather:
    """Scenario 1 & 2 — current weather retrieval."""

    def test_get_weather_with_valid_coordinates(self, client, db_session):
        """Valid saved coordinates → 200 with weather data."""
        _create_user(db_session, latitude=59.93, longitude=30.36)

        with (
            patch("app.routers.weather.fetch_weather") as mock_fetch,
            patch("app.routers.weather.get_city_name", return_value="Saint Petersburg"),
        ):
            mock_fetch.return_value = MOCK_WEATHER

            resp = client.get("/weather/")

        assert resp.status_code == 200
        data = resp.json()
        assert data["temperature"] == 20.5
        assert data["feels_like"] == 19.0
        assert data["humidity"] == 65
        assert data["weather_code"] == 2
        assert data["weather_description"] == "Partly cloudy"
        assert data["wind_speed"] == 12.3
        assert data["latitude"] == 59.93
        assert data["longitude"] == 30.36
        assert data["temperature_unit"] == "°C"
        assert data["city_name"] == "Saint Petersburg"

    def test_get_weather_no_location_saved(self, client, db_session):
        """No coordinates saved → 404."""
        _create_user(db_session, latitude=None, longitude=None)

        resp = client.get("/weather/")
        assert resp.status_code == 404
        assert "Location not set" in resp.json()["detail"]

    def test_get_weather_user_not_found(self, client):
        """No user record at all → 404."""
        resp = client.get("/weather/")
        assert resp.status_code == 404
        assert "Location not set" in resp.json()["detail"]

    def test_get_weather_external_service_failure(self, client, db_session):
        """Open-Meteo returns None → 502."""
        _create_user(db_session, latitude=59.93, longitude=30.36)

        with patch("app.routers.weather.fetch_weather") as mock_fetch:
            mock_fetch.return_value = None

            resp = client.get("/weather/")

        assert resp.status_code == 502
        assert "Failed to fetch weather data" in resp.json()["detail"]


# ===================================================================
# POST /weather/location
# ===================================================================


class TestSaveLocation:
    """Scenario 3 — saving user location manually."""

    def test_save_valid_coordinates(self, client, db_session):
        """Valid lat/lon → 200, city auto-resolved from coordinates."""
        _create_user(db_session)

        with patch("app.routers.weather.get_city_name", return_value="Москва"):
            resp = client.post("/weather/location", json={"latitude": 55.75, "longitude": 37.62})

        assert resp.status_code == 200
        data = resp.json()
        assert data["latitude"] == 55.75
        assert data["longitude"] == 37.62
        assert data["city"] == "Москва"

        # Verify persistence
        user = db_session.query(User).filter(User.id == 1).first()
        assert user.latitude == 55.75
        assert user.longitude == 37.62
        assert user.city == "Москва"

    def test_save_and_update_coordinates(self, client, db_session):
        """Saving again overwrites previous coordinates and city."""
        _create_user(db_session, latitude=59.93, longitude=30.36)

        with patch("app.routers.weather.get_city_name", return_value="Москва"):
            resp = client.post(
                "/weather/location",
                json={"latitude": 55.75, "longitude": 37.62},
            )
        assert resp.status_code == 200
        assert resp.json()["latitude"] == 55.75
        assert resp.json()["city"] == "Москва"

        user = db_session.query(User).filter(User.id == 1).first()
        assert user.latitude == 55.75
        assert user.city == "Москва"

        # Update again — city changes with new coordinates
        with patch("app.routers.weather.get_city_name", return_value="Санкт-Петербург"):
            resp = client.post(
                "/weather/location",
                json={"latitude": 59.93, "longitude": 30.36},
            )
        assert resp.status_code == 200
        assert resp.json()["city"] == "Санкт-Петербург"

        user = db_session.query(User).filter(User.id == 1).first()
        assert user.city == "Санкт-Петербург"

    def test_save_with_explicit_city(self, client, db_session):
        """City provided in POST → saved as-is, Nominatim not called."""
        _create_user(db_session)

        resp = client.post(
            "/weather/location",
            json={"latitude": 55.75, "longitude": 37.62, "city": "Москва"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["latitude"] == 55.75
        assert data["longitude"] == 37.62
        assert data["city"] == "Москва"

        user = db_session.query(User).filter(User.id == 1).first()
        assert user.city == "Москва"

    # --- Validation: out-of-range ---

    def test_save_latitude_above_90(self, client):
        """Latitude > 90 → 422."""
        resp = client.post("/weather/location", json={"latitude": 100, "longitude": 30.0})
        assert resp.status_code == 422

    def test_save_latitude_below_neg90(self, client):
        """Latitude < -90 → 422."""
        resp = client.post("/weather/location", json={"latitude": -100, "longitude": 30.0})
        assert resp.status_code == 422

    def test_save_longitude_above_180(self, client):
        """Longitude > 180 → 422."""
        resp = client.post("/weather/location", json={"latitude": 50.0, "longitude": 200})
        assert resp.status_code == 422

    def test_save_longitude_below_neg180(self, client):
        """Longitude < -180 → 422."""
        resp = client.post("/weather/location", json={"latitude": 50.0, "longitude": -200})
        assert resp.status_code == 422

    # --- Validation: type errors ---

    def test_save_latitude_as_string(self, client):
        """String instead of float → 422."""
        resp = client.post("/weather/location", json={"latitude": "invalid", "longitude": 30.0})
        assert resp.status_code == 422

    def test_save_null_coordinates(self, client):
        """Null values → 422."""
        resp = client.post("/weather/location", json={"latitude": None, "longitude": None})
        assert resp.status_code == 422

    def test_save_missing_field(self, client):
        """Missing longitude → 422."""
        resp = client.post("/weather/location", json={"latitude": 50.0})
        assert resp.status_code == 422

    def test_save_empty_body(self, client):
        """Empty JSON body → 422."""
        resp = client.post("/weather/location", json={})
        assert resp.status_code == 422


# ===================================================================
# GET /weather/location
# ===================================================================


class TestGetLocation:
    """Scenario 3 — retrieving saved location."""

    def test_get_location_when_set(self, client, db_session):
        """Saved coordinates → 200 with coordinates."""
        _create_user(db_session, latitude=59.93, longitude=30.36)

        resp = client.get("/weather/location")
        assert resp.status_code == 200
        data = resp.json()
        assert data["latitude"] == 59.93
        assert data["longitude"] == 30.36
        assert data["city"] is None

    def test_get_location_with_city(self, client, db_session):
        """Saved coordinates with city → 200 with city."""
        user = db_session.query(User).filter(User.id == 1).first()
        if not user:
            user = User(id=1, telegram_id="123456789", username="testuser")
            db_session.add(user)
        user.latitude = 55.75
        user.longitude = 37.62
        user.city = "Москва"
        db_session.commit()

        resp = client.get("/weather/location")
        assert resp.status_code == 200
        data = resp.json()
        assert data["latitude"] == 55.75
        assert data["longitude"] == 37.62
        assert data["city"] == "Москва"

    def test_get_location_not_set(self, client, db_session):
        """User exists but no coordinates → 200 with nulls."""
        _create_user(db_session, latitude=None, longitude=None)

        resp = client.get("/weather/location")
        assert resp.status_code == 200
        data = resp.json()
        assert data["latitude"] is None
        assert data["longitude"] is None
        assert data["city"] is None

    def test_get_location_user_not_found(self, client):
        """No user record → 200 with nulls."""
        resp = client.get("/weather/location")
        assert resp.status_code == 200
        data = resp.json()
        assert data["latitude"] is None
        assert data["longitude"] is None
        assert data["city"] is None
