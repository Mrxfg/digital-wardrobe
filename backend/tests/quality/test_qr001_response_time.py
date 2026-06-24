"""
QRT-001: API Response Time Test
Quality Requirement: All API endpoints must respond in < 3 seconds.

This test verifies that critical endpoints meet the response time threshold.
"""
import time

import pytest

QR001_THRESHOLD_SECONDS = 3.0  # Maximum allowed response time


class TestQR001ResponseTime:
    """Automated test for QR-001: API Response Time."""

    def test_get_items_response_time(self, client):
        """
        QRT-001: GET /clothes/ must respond within 3 seconds.

        Given the backend is running
        When a GET request is sent to /clothes/
        Then the response time must be < 3 seconds
        """
        start_time = time.time()
        response = client.get("/clothes/")
        elapsed_time = time.time() - start_time

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert elapsed_time < QR001_THRESHOLD_SECONDS, (
            f"QRT-001 FAILED: Response took {elapsed_time:.2f}s, "
            f"threshold is {QR001_THRESHOLD_SECONDS}s"
        )
        print(
            f"✓ QRT-001 PASSED: Response time "
            f"{elapsed_time:.2f}s < {QR001_THRESHOLD_SECONDS}s"
        )

    def test_health_endpoint_response_time(self, client):
        """QRT-001: Health endpoint must respond quickly."""
        start_time = time.time()
        response = client.get("/health")
        elapsed_time = time.time() - start_time

        # Health endpoint should be even faster (< 1 second)
        assert elapsed_time < 1.0, f"Health check too slow: {elapsed_time:.2f}s"
