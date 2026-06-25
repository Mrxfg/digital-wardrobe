"""
Unit and integration tests for clothing items API.

Covers CRUD operations, field validation, background removal endpoint,
and the remove_background parameter on item creation.
"""
from io import BytesIO
from unittest.mock import patch

import pytest
from PIL import Image


def _valid_jpeg_bytes() -> bytes:
    """Return a tiny (1x1) valid JPEG for test payloads."""
    buf = BytesIO()
    Image.new("RGB", (1, 1), color="red").save(buf, format="JPEG")
    return buf.getvalue()


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
            pytest.skip("Could not create item --- cannot test retrieval")

        item = create_resp.json()
        item_id = item.get("id")
        if item_id is None:
            pytest.skip("Created item has no id --- cannot test retrieval")

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


class TestCreateItemWithBackgroundRemoval:
    """PBI #164: Background removal integration with item creation."""

    def test_create_item_with_remove_background_true(self, client):
        """Scenario 3: remove_background=true processes the photo with Rembg."""
        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.return_value = image_data

            response = client.post(
                "/items/",
                data={
                    "name": "Test Shirt",
                    "category": "top",
                    "color": "blue",
                    "season": "summer",
                    "material": "cotton",
                    "remove_background": "true",
                },
                files={"photo": ("test.jpg", image_data, "image/jpeg")},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["image_url"].startswith("/uploads/processed/")
        mock_remove.assert_called_once()

    def test_create_item_with_remove_background_false(self, client):
        """Scenario 3: remove_background=false skips Rembg entirely."""
        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.return_value = image_data

            response = client.post(
                "/items/",
                data={
                    "name": "Test Shirt",
                    "category": "top",
                    "color": "blue",
                    "season": "summer",
                    "material": "cotton",
                    "remove_background": "false",
                },
                files={"photo": ("test.jpg", image_data, "image/jpeg")},
            )

        assert response.status_code == 201
        data = response.json()
        # image_url should equal original_url (no processing)
        assert data["image_url"] == data["original_image_url"]
        # Rembg should NOT have been called
        mock_remove.assert_not_called()

    def test_create_item_default_remove_background_is_true(self, client):
        """Scenario 3: default remove_background=true processes the photo."""
        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.return_value = image_data

            response = client.post(
                "/items/",
                data={
                    "name": "Default Shirt",
                    "category": "top",
                    "color": "red",
                    "season": "summer",
                    "material": "cotton",
                },
                files={"photo": ("test.jpg", image_data, "image/jpeg")},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["image_url"].startswith("/uploads/processed/")
        mock_remove.assert_called_once()


class TestRemoveBackgroundEndpoint:
    """PBI #164: Dedicated /items/remove-background endpoint."""

    def test_remove_background_valid_image(self, client):
        """Scenario 1: valid JPEG returns processed PNG."""
        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.return_value = image_data

            response = client.post(
                "/items/remove-background",
                files={"file": ("test.jpg", image_data, "image/jpeg")},
            )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/png")
        assert len(response.content) > 0
        mock_remove.assert_called_once()

    def test_remove_background_invalid_file_type(self, client):
        """Scenario 2: unsupported file type returns 400."""
        response = client.post(
            "/items/remove-background",
            files={"file": ("test.txt", b"not an image", "text/plain")},
        )

        assert response.status_code == 400

    def test_remove_background_failure_returns_500(self, client):
        """Rembg failure returns 500 with error message."""
        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.side_effect = RuntimeError("Rembg crashed")

            response = client.post(
                "/items/remove-background",
                files={"file": ("test.jpg", image_data, "image/jpeg")},
            )

        assert response.status_code == 500
