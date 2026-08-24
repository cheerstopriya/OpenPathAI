"""Contract tests for the health endpoint."""

import os
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

API_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = API_ROOT / "src"
sys.path.insert(0, str(SOURCE_ROOT))

from openpath_api.config import get_settings  # noqa: E402
from openpath_api.main import create_app  # noqa: E402


class HealthEndpointTest(unittest.TestCase):
    """Verify the public status code and JSON contract."""

    def setUp(self) -> None:
        os.environ["OPENPATH_ENVIRONMENT"] = "test"
        get_settings.cache_clear()
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        self.client.close()
        os.environ.pop("OPENPATH_ENVIRONMENT", None)
        get_settings.cache_clear()

    def test_health_returns_expected_contract(self) -> None:
        response = self.client.get("/api/v1/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "service": "OpenPath AI API",
                "version": "0.1.0",
                "environment": "test",
            },
        )

    def test_unknown_route_returns_not_found(self) -> None:
        response = self.client.get("/api/v1/does-not-exist")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()

