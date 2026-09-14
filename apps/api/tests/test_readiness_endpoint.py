"""Public API contract tests for repository readiness analysis."""

import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT / "src"))

from openpath_api.integrations.github.dependencies import get_github_client  # noqa: E402
from openpath_api.integrations.github.models import (  # noqa: E402
    GitHubCommunityProfileDto,
    GitHubOwnerDto,
    GitHubRepositoryDto,
)
from openpath_api.main import create_app  # noqa: E402


class FakeReadinessGitHubClient:
    async def get_repository(self, _reference: object) -> GitHubRepositoryDto:
        return GitHubRepositoryDto(
            owner=GitHubOwnerDto(login="example"),
            name="project",
            full_name="example/project",
            html_url="https://github.com/example/project",
            stargazers_count=10,
            forks_count=2,
            default_branch="main",
            archived=False,
            disabled=False,
            visibility="public",
            topics=[],
            pushed_at=datetime.now(UTC),
        )

    async def get_community_profile(self, _reference: object) -> GitHubCommunityProfileDto:
        return GitHubCommunityProfileDto(health_percentage=0, files={})

    async def list_pull_requests(self, _reference: object, *, limit: int) -> list:
        return []

    async def list_open_issues(self, _reference: object, *, limit: int) -> list:
        return []


class ReadinessEndpointTest(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.app.dependency_overrides[get_github_client] = lambda: FakeReadinessGitHubClient()
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.client.close()
        self.app.dependency_overrides.clear()

    def test_returns_explainable_readiness_contract(self) -> None:
        response = self.client.post(
            "/api/v1/repositories/readiness",
            json={"repository_url": "https://github.com/example/project"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["repository_full_name"], "example/project")
        self.assertEqual(body["formula_version"], "1.0.0")
        self.assertEqual(len(body["dimensions"]), 6)
        self.assertEqual(body["coverage_percentage"], 55)
        self.assertEqual(body["confidence"], "low")
        self.assertIsNone(
            next(item for item in body["dimensions"] if item["key"] == "review_responsiveness")[
                "score"
            ]
        )

    def test_rejects_untrusted_repository_url_before_github_calls(self) -> None:
        response = self.client.post(
            "/api/v1/repositories/readiness",
            json={"repository_url": "http://127.0.0.1/private"},
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("github.com", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
