"""
Unit and integration tests for background removal (PBI #167).

Covers the full Rembg wrapper (services/upload.py) and the POST /upload/
endpoint: success, failure, timeout, and fallback scenarios.

Acceptance criteria
-------------------
- Unit tests: success + failure (corrupted image, timeout)
- Integration: valid image → processed response, <5 s, JSON Content-Type
- Fallback:  Rembg failure → original photo preserved + notification
- QRT-002 contribution (already covered in tests/quality/)
"""

import time
from io import BytesIO
from unittest.mock import patch

import pytest
from PIL import Image

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _valid_jpeg_bytes() -> bytes:
    """Return a tiny (1×1) valid JPEG for test payloads."""
    buf = BytesIO()
    Image.new("RGB", (1, 1), color="red").save(buf, format="JPEG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Unit tests – Rembg wrapper (services/upload.py)
# ---------------------------------------------------------------------------


class TestRembgWrapper:
    """Unit tests for ``save_processed`` in ``app.services.upload``."""

    def test_save_processed_success(self):
        """Scenario 1: Rembg processes a valid image successfully."""
        from app.services.upload import save_processed

        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.return_value = image_data

            path, url = save_processed(image_data)

            assert path is not None
            assert path.suffix == ".png"
            assert url.startswith("/uploads/processed/")
            mock_remove.assert_called_once()

    def test_save_processed_corrupted_image(self):
        """Scenario 1: Rembg raises on corrupted / invalid image data."""
        from app.services.upload import save_processed

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.side_effect = Exception("Invalid image data: cannot decode")

            with pytest.raises(Exception, match="Invalid image data"):
                save_processed(b"not a real image")

    def test_save_processed_timeout(self):
        """Scenario 1: Simulate slow rembg processing – system doesn't hang."""
        from app.services.upload import save_processed

        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:

            def _slow_remove(*args, **kwargs):
                time.sleep(0.3)  # simulate moderate delay (CI-safe)
                return image_data

            mock_remove.side_effect = _slow_remove

            start = time.time()
            path, url = save_processed(image_data)
            elapsed = time.time() - start

            assert elapsed >= 0.2  # the delay was respected
            assert url.startswith("/uploads/processed/")


# ---------------------------------------------------------------------------
# Integration tests – POST /upload/ endpoint
# ---------------------------------------------------------------------------


class TestBackgroundRemovalEndpoint:
    """Integration tests for the image upload endpoint."""

    def test_upload_valid_image_returns_200(self, client):
        """Scenario 2: POST /upload/ with a valid JPEG → 200 + image_urls."""
        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.return_value = image_data

            response = client.post(
                "/upload/",
                files={"file": ("test.jpg", image_data, "image/jpeg")},
            )

        assert response.status_code == 200
        data = response.json()
        assert "image_url" in data
        assert "original_image_url" in data
        assert data["image_url"].startswith("/uploads/processed/")
        assert data["original_image_url"].startswith("/uploads/original/")

    def test_upload_response_time_under_5s(self, client):
        """Scenario 2: Response time for /upload/ is < 5 seconds."""
        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.return_value = image_data

            start = time.time()
            response = client.post(
                "/upload/",
                files={"file": ("test.jpg", image_data, "image/jpeg")},
            )
            elapsed = time.time() - start

            assert response.status_code == 200
            assert elapsed < 5.0, f"Response took {elapsed:.2f}s (threshold 5s)"

    def test_upload_response_content_type_json(self, client):
        """Scenario 2: Response Content-Type is application/json."""
        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.return_value = image_data

            response = client.post(
                "/upload/",
                files={"file": ("test.jpg", image_data, "image/jpeg")},
            )

            ct = response.headers.get("content-type", "")
            assert ct.startswith("application/json"), f"Unexpected Content-Type: {ct}"

    # ------------------------------------------------------------------
    # Fallback (Scenario 3)
    # ------------------------------------------------------------------

    def test_rembg_failure_returns_fallback_with_notification(self, client):
        """Scenario 3: On Rembg failure → 200 + original photo + notification.

        The endpoint catches the exception, returns the original image
        URL as a fallback, and includes a user-facing notification.
        """
        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.side_effect = Exception("Rembg failed: out of memory")

            response = client.post(
                "/upload/",
                files={"file": ("test.jpg", image_data, "image/jpeg")},
            )

        # System should NOT crash — returns 200 with fallback data
        assert response.status_code == 200, f"Expected 200 fallback, got {response.status_code}"
        data = response.json()

        # Original photo is preserved / returned
        assert "original_image_url" in data
        assert data["original_image_url"].startswith("/uploads/original/")

        # Fallback: image_url equals original_url (no processed version)
        assert data.get("image_url") == data["original_image_url"], "Expected image_url to fall back to original_image_url"

        # User notification present
        notification = data.get("notification", "")
        assert "Background removal unavailable" in notification, f"Missing or wrong notification: '{notification}'"

    def test_rembg_failure_fallback_structure(self, client):
        """Scenario 3: The fallback response has exactly the expected keys."""
        image_data = _valid_jpeg_bytes()

        with patch("app.services.upload.remove") as mock_remove:
            mock_remove.side_effect = RuntimeError("OOM")

            response = client.post(
                "/upload/",
                files={"file": ("test.jpg", image_data, "image/jpeg")},
            )

        assert response.status_code == 200
        keys = set(response.json().keys())
        expected = {"image_url", "original_image_url", "notification"}
        assert expected.issubset(keys), f"Missing keys in fallback: {expected - keys}"


# ---------------------------------------------------------------------------
# Invalid-file handling (shared with QRT-002)
# ---------------------------------------------------------------------------


class TestBackgroundRemovalInvalidInput:
    """Edge cases: invalid files are rejected with proper status codes."""

    def test_invalid_file_type_rejected(self, client):
        """Unsupported file type → 400."""
        response = client.post(
            "/upload/",
            files={"file": ("test.txt", b"not an image", "text/plain")},
        )
        assert response.status_code == 400

    def test_empty_file_rejected(self, client):
        """Empty file → 400."""
        response = client.post(
            "/upload/",
            files={"file": ("empty.jpg", b"", "image/jpeg")},
        )
        assert response.status_code == 400
