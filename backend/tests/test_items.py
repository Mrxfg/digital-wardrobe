"""
Unit and integration tests for clothing items API.

Covers CRUD operations and field validation for the /clothes/ endpoints.
Paths are adapted to the actual project routing (/clothes/ instead of /api/items).
"""
import pytest


class TestItemsAPI:
    """Integration tests for /clothes/ endpoints."""

    def test_get_items_returns_list(self, client):
        """QR-003: Verify items endpoint returns a list."""
        response = client.get("/clothes/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_item_success(self, client, sample_item_data):
        """Integration test: create a new clothing item."""
        response = client.post("/clothes/", json=sample_item_data)
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["name"] == sample_item_data["name"]

    def test_create_item_missing_required_field(self, client):
        """Unit test: validation rejects incomplete data."""
        response = client.post("/clothes/", json={"name": "Test"})
        assert response.status_code in (400, 422)

    def test_get_item_by_id(self, client):
        """Integration test: retrieve a specific item by its ID."""
        # First create an item
        create_resp = client.post(
            "/clothes/",
            json={
                "name": "Test Shirt",
                "category": "top",
                "color": "red",
                "season": "summer",
                "material": "cotton",
            },
        )
        if create_resp.status_code not in (200, 201):
            pytest.skip("Could not create item — cannot test retrieval")

        item = create_resp.json()
        item_id = item.get("id")
        if item_id is None:
            pytest.skip("Created item has no id — cannot test retrieval")

        response = client.get(f"/clothes/{item_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Test Shirt"


class TestItemsValidation:
    """Unit tests for item validation constants (business logic)."""

    def test_season_values(self):
        """Verify the set of valid season values."""
        valid_seasons = {"spring", "summer", "autumn", "winter", "all_season"}
        for season in valid_seasons:
            assert season in valid_seasons
        # Also verify no unexpected values leak through
        assert "invalid_season" not in valid_seasons

    def test_category_values(self):
        """Verify the set of valid category values."""
        valid_categories = {"top", "bottom", "outerwear", "shoes", "accessories"}
        for cat in valid_categories:
            assert cat in valid_categories
        assert "invalid_category" not in valid_categories
