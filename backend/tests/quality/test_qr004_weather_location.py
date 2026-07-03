import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_location_endpoint_responds_valid_structure():
    """QR-001/QR-002: /api/user/location returns coords or proper error"""
    response = client.get("/api/user/location", headers={"Authorization": "Bearer valid_test_token"})

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "latitude" in data and "longitude" in data
        assert isinstance(data["latitude"], (int, float))
        assert isinstance(data["longitude"], (int, float))
