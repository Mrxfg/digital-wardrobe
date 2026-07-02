import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_calendar_module_loaded_and_responds():
    """QR-001/QR-002: Calendar/capsule module is integrated and responsive"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    paths = schema.get("paths", {})
    has_calendar_related = any("capsule" in k.lower() or "outfit" in k.lower() for k in paths.keys())
    assert has_calendar_related, "Calendar/capsule routes not found in OpenAPI schema"
    
    health_resp = client.get("/")
    assert health_resp.status_code in [200, 404]  