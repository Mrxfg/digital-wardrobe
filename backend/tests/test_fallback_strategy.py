"""
Tests for PBI #165: Fallback strategy on Rembg failure.

Acceptance criteria
-------------------
Scenario 1: Rembg fails gracefully
  - Original photo is saved (no data loss)
  - User receives notification: "Background removal unavailable"
  - Error is logged for debugging

Scenario 2: Corrupted image → fallback to original photo

Scenario 3: Timeout handling → fallback to original + notification
"""
import logging
from io import BytesIO
from unittest.mock import patch

import pytest
from PIL import Image


def _valid_jpeg_bytes() -> bytes:
    """Return a tiny (1×1) valid JPEG for test payloads."""
    buf = BytesIO()
    Image.new("RGB", (1, 1), color="red").save(buf, format="JPEG")
    return buf.getvalue()


class TestRembgFallback:
    """PBI-165: Fallback strategy when Rembg fails."""

    def test_rembg_failure_preserves_original_photo(self, client):
        """
        Scenario 1: Rembg fails → original photo returned.

        Given Rembg throws an error
        When the user uploads a photo
        Then the original photo is preserved (no data loss)
        """
        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.side_effect = Exception("Rembg failed: out of memory")

            response = client.post(
                "/upload/",
                files={"file": ("test.jpg", image_data, "image/jpeg")},
            )

        # Original photo is returned
        assert response.status_code == 200
        data = response.json()
        assert "original_image_url" in data
        assert data["original_image_url"].startswith("/uploads/original/")

    def test_rembg_failure_returns_notification(self, client):
        """
        Scenario 1: user receives notification that rembg is unavailable.

        When Rembg fails
        Then the response includes a user-facing notification
        """
        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.side_effect = RuntimeError("OOM")

            response = client.post(
                "/upload/",
                files={"file": ("test.jpg", image_data, "image/jpeg")},
            )

        assert response.status_code == 200
        notification = response.json().get("notification", "")
        assert "Background removal unavailable" in notification, (
            f"Missing notification: '{notification}'"
        )

    def test_rembg_failure_fallback_to_original_url(self, client):
        """
        Scenario 1: image_url falls back to original_image_url.
        """
        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.side_effect = Exception("fail")

            response = client.post(
                "/upload/",
                files={"file": ("test.jpg", image_data, "image/jpeg")},
            )

        assert response.status_code == 200
        data = response.json()
        # Both URLs should point to the original (no processed version)
        assert data["image_url"] == data["original_image_url"]

    def test_rembg_failure_logs_error(self, client, caplog):
        """
        Scenario 1: error is logged for debugging.

        When Rembg fails
        Then the error is written to the application log
        """
        image_data = _valid_jpeg_bytes()
        caplog.set_level(logging.ERROR)

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.side_effect = ValueError("model crash")

            client.post(
                "/upload/",
                files={"file": ("test.jpg", image_data, "image/jpeg")},
            )

        # Verify error was logged
        assert any(
            "Background removal failed" in record.message
            for record in caplog.records
        ), "Error was not logged"

    def test_corrupted_image_fallback(self, client):
        """
        Scenario 2: corrupted image → system falls back to original.

        Given Rembg receives corrupted image data
        When processing is attempted
        Then the system falls back to the original photo
        """
        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.side_effect = RuntimeError("Cannot decode image")

            response = client.post(
                "/upload/",
                files={"file": ("test.jpg", image_data, "image/jpeg")},
            )

        assert response.status_code == 200
        data = response.json()
        assert "original_image_url" in data
        assert "notification" in data

    def test_timeout_fallback(self, client):
        """
        Scenario 3: timeout → fallback to original + notification.

        Given Rembg processing takes too long
        When a timeout occurs
        Then the system falls back to the original photo
        And the user is notified
        """
        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            # Simulate a timeout-like failure
            mock_remove.side_effect = TimeoutError("Rembg processing timed out")

            response = client.post(
                "/upload/",
                files={"file": ("test.jpg", image_data, "image/jpeg")},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["image_url"] == data["original_image_url"], (
            "Should fallback to original on timeout"
        )
        notification = data.get("notification", "")
        assert "Background removal unavailable" in notification


class TestInvalidInput:
    """PBI-165: Edge cases — invalid input is rejected gracefully."""

    def test_unsupported_file_type(self, client):
        """Unsupported file type → 400, not 500."""
        response = client.post(
            "/upload/",
            files={"file": ("test.txt", b"not an image", "text/plain")},
        )
        assert response.status_code == 400

    def test_empty_file(self, client):
        """Empty file → 400."""
        response = client.post(
            "/upload/",
            files={"file": ("empty.jpg", b"", "image/jpeg")},
        )
        assert response.status_code == 400
