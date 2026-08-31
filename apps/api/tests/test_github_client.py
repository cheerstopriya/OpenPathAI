"""Adapter tests using HTTPX's in-memory transport instead of live GitHub."""

import sys
import unittest
from pathlib import Path

import httpx

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT / "src"))

from openpath_api.domain.repositories.reference import RepositoryReference  # noqa: E402
from openpath_api.integrations.github.client import GitHubClient  # noqa: E402
from openpath_api.integrations.github.errors import (  # noqa: E402
    GitHubRateLimited,
    GitHubRepositoryNotFound,
)


class GitHubClientTest(unittest.IsolatedAsyncioTestCase):
    async def test_fetches_and_validates_repository(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.host, "api.github.com")
            self.assertEqual(request.url.path, "/repos/angular/angular")
            return httpx.Response(
                200,
                json={
                    "owner": {"login": "angular"},
                    "name": "angular",
                    "full_name": "angular/angular",
                    "description": "Web framework",
                    "html_url": "https://github.com/angular/angular",
                    "language": "TypeScript",
                    "stargazers_count": 100,
                    "forks_count": 20,
                    "default_branch": "main",
                    "archived": False,
                    "disabled": False,
                    "visibility": "public",
                    "topics": ["typescript"],
                    "license": {"spdx_id": "MIT"},
                    "pushed_at": "2026-08-20T10:00:00Z",
                    "ignored_external_field": "not exposed",
                },
            )

        async with httpx.AsyncClient(
            base_url="https://api.github.com",
            transport=httpx.MockTransport(handler),
        ) as http_client:
            result = await GitHubClient(http_client).get_repository(
                RepositoryReference(owner="angular", name="angular")
            )

        self.assertEqual(result.full_name, "angular/angular")
        self.assertEqual(result.license.spdx_id if result.license else None, "MIT")

    async def test_maps_not_found_without_live_request(self) -> None:
        transport = httpx.MockTransport(lambda _: httpx.Response(404, json={"message": "No"}))

        async with httpx.AsyncClient(
            base_url="https://api.github.com",
            transport=transport,
        ) as http_client:
            with self.assertRaises(GitHubRepositoryNotFound):
                await GitHubClient(http_client).get_repository(
                    RepositoryReference(owner="missing", name="repository")
                )

    async def test_maps_rate_limit_and_preserves_reset_time(self) -> None:
        transport = httpx.MockTransport(
            lambda _: httpx.Response(429, headers={"x-ratelimit-reset": "1800000000"})
        )

        async with httpx.AsyncClient(
            base_url="https://api.github.com",
            transport=transport,
        ) as http_client:
            with self.assertRaises(GitHubRateLimited) as context:
                await GitHubClient(http_client).get_repository(
                    RepositoryReference(owner="angular", name="angular")
                )

        self.assertEqual(context.exception.reset_at, "1800000000")


if __name__ == "__main__":
    unittest.main()
