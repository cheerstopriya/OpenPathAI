"""Public API contract tests for repository preview."""

import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT / "src"))

from openpath_api.integrations.github.dependencies import get_github_client  # noqa: E402
from openpath_api.integrations.github.models import (  # noqa: E402
    GitHubLicenseDto,
    GitHubOwnerDto,
    GitHubRepositoryDto,
)
from openpath_api.main import create_app  # noqa: E402


class FakeGitHubClient:
    async def get_repository(self, _reference: object) -> GitHubRepositoryDto:
        return GitHubRepositoryDto(
            owner=GitHubOwnerDto(login="angular"),
            name="angular",
            full_name="angular/angular",
            description="Web framework",
            html_url="https://github.com/angular/angular",
            language="TypeScript",
            stargazers_count=100,
            forks_count=20,
            default_branch="main",
            archived=False,
            disabled=False,
            visibility="public",
            topics=["typescript"],
            license=GitHubLicenseDto(spdx_id="MIT"),
            pushed_at=datetime(2026, 8, 20, 10, 0, tzinfo=UTC),
        )


class RepositoryPreviewEndpointTest(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.app.dependency_overrides[get_github_client] = lambda: FakeGitHubClient()
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.client.close()
        self.app.dependency_overrides.clear()

    def test_returns_small_stable_repository_contract(self) -> None:
        response = self.client.post(
            "/api/v1/repositories/preview",
            json={"repository_url": "https://github.com/angular/angular"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "owner": "angular",
                "name": "angular",
                "full_name": "angular/angular",
                "description": "Web framework",
                "html_url": "https://github.com/angular/angular",
                "primary_language": "TypeScript",
                "stars": 100,
                "forks": 20,
                "default_branch": "main",
                "archived": False,
                "disabled": False,
                "visibility": "public",
                "topics": ["typescript"],
                "license_spdx": "MIT",
                "pushed_at": "2026-08-20T10:00:00Z",
            },
        )

    def test_rejects_non_github_url_before_calling_adapter(self) -> None:
        response = self.client.post(
            "/api/v1/repositories/preview",
            json={"repository_url": "http://127.0.0.1/private"},
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("github.com", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
