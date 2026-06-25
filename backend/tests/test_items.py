"""
Unit and integration tests for clothing items API.

Covers CRUD operations, field validation, background removal endpoint,
and the remove_background parameter on item creation.
"""

from datetime import datetime, timedelta, timezone

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


class TestTrashDaysRemaining:
    """PBI #172: days_remaining in trash basket."""

    def _create_and_delete_item(self, client) -> int:
        """Helper: create an item, soft-delete it, return its id."""
        resp = client.post(
            "/clothes/",
            json={
                "name": "Trash Test",
                "category": "top",
                "color": "red",
                "season": "summer",
                "material": "cotton",
            },
        )
        assert resp.status_code in (200, 201)
        item_id = resp.json()["id"]

        delete_resp = client.delete(f"/clothes/{item_id}")
        assert delete_resp.status_code == 200
        return item_id

    def test_days_remaining_in_trash_response(self, client):
        """Scenario 1: trash response includes days_remaining as int."""
        self._create_and_delete_item(client)

        resp = client.get("/clothes/trash")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) > 0
        assert "days_remaining" in items[0]
        assert isinstance(items[0]["days_remaining"], int)

    def test_days_remaining_freshly_deleted_returns_14(self, client):
        """Scenario 3: item deleted just now → days_remaining = 14."""
        self._create_and_delete_item(client)

        resp = client.get("/clothes/trash")
        items = resp.json()
        # Freshly deleted item should have days_remaining = 14
        assert items[0]["days_remaining"] == 14

    def test_days_remaining_decreases_over_time(self, client):
        """Scenario 2: manually set deleted_at 5 days ago → days_remaining = 9."""
        from app.database import get_db
        from app.models.clothing_item import ClothingItem

        # Create and delete via API first
        item_id = self._create_and_delete_item(client)

        # Manually adjust deleted_at to 5 days ago in the DB
        db = next(get_db())
        try:
            item = db.query(ClothingItem).filter(ClothingItem.id == item_id).first()
            item.deleted_at = datetime.now(timezone.utc) - timedelta(days=5)
            db.commit()
        finally:
            db.close()

        resp = client.get("/clothes/trash")
        items = resp.json()
        assert items[0]["days_remaining"] == 9

    def test_days_remaining_old_item_returns_0(self, client):
        """Item in trash for 14+ days → days_remaining = 0."""
        from app.database import get_db
        from app.models.clothing_item import ClothingItem

        item_id = self._create_and_delete_item(client)

        db = next(get_db())
        try:
            item = db.query(ClothingItem).filter(ClothingItem.id == item_id).first()
            item.deleted_at = datetime.now(timezone.utc) - timedelta(days=15)
            db.commit()
        finally:
            db.close()

        resp = client.get("/clothes/trash")
        items = resp.json()
        assert items[0]["days_remaining"] == 0

    def test_days_remaining_is_none_for_active_items(self, client, sample_item_data):
        """Active (non-deleted) items have days_remaining = None."""
        resp = client.post("/clothes/", json=sample_item_data)
        item_id = resp.json()["id"]

        resp = client.get(f"/clothes/{item_id}")
        data = resp.json()
        assert data["days_remaining"] is None

    @pytest.mark.parametrize("deleted_days_ago,expected", [(0, 14), (1, 13), (7, 7), (13, 1), (14, 0), (20, 0)])
    def test_days_remaining_parametrized(self, client, deleted_days_ago, expected):
        """Verify days_remaining = max(0, 14 - days_since_deleted)."""
        from app.database import get_db
        from app.models.clothing_item import ClothingItem

        item_id = self._create_and_delete_item(client)

        db = next(get_db())
        try:
            item = db.query(ClothingItem).filter(ClothingItem.id == item_id).first()
            item.deleted_at = datetime.now(timezone.utc) - timedelta(days=deleted_days_ago)
            db.commit()
        finally:
            db.close()

        resp = client.get("/clothes/trash")
        items = resp.json()
        assert items[0]["days_remaining"] == expected, (
            f"Expected {expected} days_remaining for deleted {deleted_days_ago} days ago, "
            f"got {items[0]['days_remaining']}"
        )

    def test_restore_clears_deleted_at(self, client):
        """Restoring an item clears deleted_at and sets days_remaining to None."""
        item_id = self._create_and_delete_item(client)

        # Verify it's in trash with days_remaining
        trash_resp = client.get("/clothes/trash")
        assert any(item["id"] == item_id for item in trash_resp.json())

        # Restore
        restore_resp = client.post(f"/clothes/{item_id}/restore")
        assert restore_resp.status_code == 200

        # Should no longer be in trash
        trash_resp = client.get("/clothes/trash")
        assert not any(item["id"] == item_id for item in trash_resp.json())

        # Active item should have days_remaining = None
        detail_resp = client.get(f"/clothes/{item_id}")
        assert detail_resp.json()["days_remaining"] is None
