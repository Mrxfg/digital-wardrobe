"""
Unit and integration tests for capsules API.

Covers CRUD operations, item management, and validation.
"""

import pytest


class TestCapsulesCreate:
    """Tests for POST /capsules/ — create a capsule."""

    def test_create_capsule_success(self, client, sample_item_data):
        """Create a capsule with valid data returns 201."""
        resp = client.post("/capsules/", json={"name": "Summer Capsule"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Summer Capsule"
        assert data["items"] == []
        assert "description" not in data
        assert "season" not in data

    def test_create_capsule_with_items_and_no_description_in_response(self, client):
        """Create capsule with items — response contains only lightweight fields."""
        item1 = client.post(
            "/clothes/",
            json={
                "name": "Shirt",
                "category": "top",
                "color": "blue",
                "season": "summer",
                "material": "cotton",
            },
        ).json()
        resp = client.post(
            "/capsules/",
            json={"name": "Work Capsule", "items": [item1["id"]]},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Work Capsule"
        assert "description" not in data
        assert "season" not in data

    def test_create_capsule_with_items(self, client):
        """Create a capsule with clothing item IDs."""
        # Create two clothing items first
        item1 = client.post(
            "/clothes/",
            json={
                "name": "Shirt",
                "category": "top",
                "color": "blue",
                "season": "summer",
                "material": "cotton",
            },
        ).json()
        item2 = client.post(
            "/clothes/",
            json={
                "name": "Pants",
                "category": "bottom",
                "color": "black",
                "season": "summer",
                "material": "denim",
            },
        ).json()

        resp = client.post(
            "/capsules/",
            json={"name": "Capsule with Items", "items": [item1["id"], item2["id"]]},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["items"]) == 2
        item_ids = {item["id"] for item in data["items"]}
        assert item_ids == {item1["id"], item2["id"]}

    def test_create_capsule_missing_name(self, client):
        """Missing required field name → 422."""
        resp = client.post("/capsules/", json={})
        assert resp.status_code == 422

    def test_create_capsule_too_many_items(self, client):
        """More than 8 items → 400."""
        resp = client.post("/capsules/", json={"name": "Full", "items": list(range(1, 10))})
        assert resp.status_code == 400
        assert "maximum 8" in resp.json()["detail"].lower()

    def test_create_capsule_invalid_item_id(self, client):
        """Non-existent item ID → 404."""
        resp = client.post("/capsules/", json={"name": "Bad", "items": [99999]})
        assert resp.status_code == 404


class TestCapsulesList:
    """Tests for GET /capsules/ — list capsules."""

    def test_list_capsules_empty(self, client):
        """No capsules → empty list."""
        resp = client.get("/capsules/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_capsules(self, client):
        """Multiple capsules returned."""
        client.post("/capsules/", json={"name": "A"})
        client.post("/capsules/", json={"name": "B"})
        resp = client.get("/capsules/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    def test_list_capsules_filter_by_name(self, client):
        """Filter by name (partial match)."""
        client.post("/capsules/", json={"name": "Summer Capsule"})
        client.post("/capsules/", json={"name": "Winter Capsule"})
        resp = client.get("/capsules/?name=summer")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Summer Capsule"


class TestCapsulesGet:
    """Tests for GET /capsules/{id} — get single capsule."""

    def test_get_capsule_by_id(self, client):
        """Get capsule returns correct data."""
        create_resp = client.post("/capsules/", json={"name": "My Capsule"})
        capsule_id = create_resp.json()["id"]

        resp = client.get(f"/capsules/{capsule_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "My Capsule"

    def test_get_capsule_not_found(self, client):
        """Non-existent capsule → 404."""
        resp = client.get("/capsules/99999")
        assert resp.status_code == 404

    def test_get_capsule_includes_items(self, client):
        """Response includes items list."""
        item = client.post(
            "/clothes/",
            json={
                "name": "Shirt",
                "category": "top",
                "color": "blue",
                "season": "summer",
                "material": "cotton",
            },
        ).json()

        create_resp = client.post("/capsules/", json={"name": "Test", "items": [item["id"]]})
        capsule_id = create_resp.json()["id"]

        resp = client.get(f"/capsules/{capsule_id}")
        assert len(resp.json()["items"]) == 1
        assert resp.json()["items"][0]["id"] == item["id"]


class TestCapsulesUpdate:
    """Tests for PATCH /capsules/{id} — update a capsule."""

    def test_update_capsule_name(self, client):
        """Update capsule name."""
        create_resp = client.post("/capsules/", json={"name": "Old Name"})
        capsule_id = create_resp.json()["id"]

        resp = client.patch(f"/capsules/{capsule_id}", json={"name": "New Name"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"

    def test_update_capsule_description(self, client):
        """Update capsule description — still succeeds but field not in response."""
        create_resp = client.post("/capsules/", json={"name": "Test"})
        capsule_id = create_resp.json()["id"]

        resp = client.patch(f"/capsules/{capsule_id}", json={"description": "Updated desc"})
        assert resp.status_code == 200
        assert "description" not in resp.json()

    def test_update_capsule_season(self, client):
        """Update capsule season — still succeeds but field not in response."""
        create_resp = client.post("/capsules/", json={"name": "Test"})
        capsule_id = create_resp.json()["id"]

        resp = client.patch(f"/capsules/{capsule_id}", json={"season": "winter"})
        assert resp.status_code == 200
        assert "season" not in resp.json()

    def test_update_capsule_not_found(self, client):
        """Update non-existent capsule → 404."""
        resp = client.patch("/capsules/99999", json={"name": "Nope"})
        assert resp.status_code == 404


class TestCapsulesDelete:
    """Tests for DELETE /capsules/{id} — delete a capsule."""

    def test_delete_capsule(self, client):
        """Delete capsule returns success."""
        create_resp = client.post("/capsules/", json={"name": "Delete Me"})
        capsule_id = create_resp.json()["id"]

        resp = client.delete(f"/capsules/{capsule_id}")
        assert resp.status_code == 200

        # Verify it's gone
        get_resp = client.get(f"/capsules/{capsule_id}")
        assert get_resp.status_code == 404

    def test_delete_capsule_not_found(self, client):
        """Delete non-existent capsule → 404."""
        resp = client.delete("/capsules/99999")
        assert resp.status_code == 404


class TestCapsuleItems:
    """Tests for capsule item management endpoints."""

    def test_add_item_to_capsule(self, client, sample_item_data):
        """Add item to capsule."""
        item = client.post("/clothes/", json=sample_item_data).json()
        capsule = client.post("/capsules/", json={"name": "Test"}).json()

        resp = client.post(f"/capsules/{capsule['id']}/items", json={"clothing_item_id": item["id"]})
        assert resp.status_code == 200
        assert resp.json()["clothing_item_id"] == item["id"]

    def test_add_duplicate_item_returns_400(self, client, sample_item_data):
        """Duplicate item → 400."""
        item = client.post("/clothes/", json=sample_item_data).json()
        capsule = client.post("/capsules/", json={"name": "Test"}).json()

        client.post(f"/capsules/{capsule['id']}/items", json={"clothing_item_id": item["id"]})
        resp = client.post(f"/capsules/{capsule['id']}/items", json={"clothing_item_id": item["id"]})
        assert resp.status_code == 400

    def test_add_item_exceeds_max(self, client):
        """More than 8 items → 400."""
        capsule = client.post("/capsules/", json={"name": "Full"}).json()

        # Create 8 items and add them
        for i in range(8):
            item = client.post(
                "/clothes/",
                json={
                    "name": f"Item {i}",
                    "category": "top",
                    "color": "blue",
                    "season": "summer",
                    "material": "cotton",
                },
            ).json()
            client.post(
                f"/capsules/{capsule['id']}/items",
                json={"clothing_item_id": item["id"]},
            )

        # 9th should fail
        item9 = client.post(
            "/clothes/",
            json={
                "name": "Item 9",
                "category": "top",
                "color": "red",
                "season": "summer",
                "material": "cotton",
            },
        ).json()
        resp = client.post(f"/capsules/{capsule['id']}/items", json={"clothing_item_id": item9["id"]})
        assert resp.status_code == 400

    def test_get_capsule_items(self, client, sample_item_data):
        """List items in capsule."""
        item = client.post("/clothes/", json=sample_item_data).json()
        capsule = client.post("/capsules/", json={"name": "Test"}).json()
        client.post(f"/capsules/{capsule['id']}/items", json={"clothing_item_id": item["id"]})

        resp = client.get(f"/capsules/{capsule['id']}/items")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["id"] == item["id"]

    def test_remove_item_from_capsule(self, client, sample_item_data):
        """Remove item from capsule."""
        item = client.post("/clothes/", json=sample_item_data).json()
        capsule = client.post("/capsules/", json={"name": "Test"}).json()
        client.post(f"/capsules/{capsule['id']}/items", json={"clothing_item_id": item["id"]})

        resp = client.delete(f"/capsules/{capsule['id']}/items/{item['id']}")
        assert resp.status_code == 200

        # Verify empty
        items_resp = client.get(f"/capsules/{capsule['id']}/items")
        assert items_resp.json() == []
