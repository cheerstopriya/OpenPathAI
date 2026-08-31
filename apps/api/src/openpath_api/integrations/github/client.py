"""Constrained, read-only GitHub REST API client."""

import httpx
from pydantic import ValidationError

from openpath_api.domain.repositories.reference import RepositoryReference
from openpath_api.integrations.github.errors import (
    GitHubRateLimited,
    GitHubRepositoryNotFound,
    GitHubUnavailable,
)
from openpath_api.integrations.github.models import GitHubRepositoryDto


class GitHubClient:
    """Fetch approved resources through a preconfigured api.github.com client."""

    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._http_client = http_client

    async def get_repository(self, reference: RepositoryReference) -> GitHubRepositoryDto:
        try:
            response = await self._http_client.get(
                f"/repos/{reference.owner}/{reference.name}",
            )
        except httpx.TimeoutException as exc:
            raise GitHubUnavailable("GitHub timed out") from exc
        except httpx.RequestError as exc:
            raise GitHubUnavailable("GitHub request failed") from exc

        if response.status_code == 404:
            raise GitHubRepositoryNotFound
        if response.status_code in {403, 429}:
            raise GitHubRateLimited(response.headers.get("x-ratelimit-reset"))
        if response.is_error:
            raise GitHubUnavailable(f"GitHub returned HTTP {response.status_code}")

        try:
            return GitHubRepositoryDto.model_validate(response.json())
        except (ValueError, ValidationError) as exc:
            raise GitHubUnavailable("GitHub returned an unexpected response") from exc
