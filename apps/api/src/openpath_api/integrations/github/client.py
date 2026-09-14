"""Constrained, read-only GitHub REST API client."""

import httpx
from pydantic import ValidationError

from openpath_api.domain.repositories.reference import RepositoryReference
from openpath_api.integrations.github.errors import (
    GitHubRateLimited,
    GitHubRepositoryNotFound,
    GitHubUnavailable,
)
from openpath_api.integrations.github.models import (
    GitHubCommunityProfileDto,
    GitHubIssueDto,
    GitHubPullRequestDto,
    GitHubPullRequestReviewDto,
    GitHubRepositoryDto,
)


class GitHubClient:
    """Fetch approved resources through a preconfigured api.github.com client."""

    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._http_client = http_client

    async def get_repository(self, reference: RepositoryReference) -> GitHubRepositoryDto:
        payload = await self._get(f"/repos/{reference.owner}/{reference.name}")
        return self._validate(GitHubRepositoryDto, payload)

    async def get_community_profile(
        self, reference: RepositoryReference
    ) -> GitHubCommunityProfileDto:
        payload = await self._get(
            f"/repos/{reference.owner}/{reference.name}/community/profile"
        )
        return self._validate(GitHubCommunityProfileDto, payload)

    async def list_pull_requests(
        self, reference: RepositoryReference, *, limit: int = 20
    ) -> list[GitHubPullRequestDto]:
        payload = await self._get(
            f"/repos/{reference.owner}/{reference.name}/pulls",
            params={"state": "all", "sort": "updated", "direction": "desc", "per_page": limit},
        )
        return self._validate_list(GitHubPullRequestDto, payload)

    async def list_pull_request_reviews(
        self, reference: RepositoryReference, pull_number: int, *, limit: int = 20
    ) -> list[GitHubPullRequestReviewDto]:
        payload = await self._get(
            f"/repos/{reference.owner}/{reference.name}/pulls/{pull_number}/reviews",
            params={"per_page": limit},
        )
        return self._validate_list(GitHubPullRequestReviewDto, payload)

    async def list_open_issues(
        self, reference: RepositoryReference, *, limit: int = 30
    ) -> list[GitHubIssueDto]:
        payload = await self._get(
            f"/repos/{reference.owner}/{reference.name}/issues",
            params={"state": "open", "sort": "updated", "direction": "desc", "per_page": limit},
        )
        return self._validate_list(GitHubIssueDto, payload)

    async def _get(self, path: str, *, params: dict[str, str | int] | None = None) -> object:
        try:
            response = await self._http_client.get(path, params=params)
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
            return response.json()
        except ValueError as exc:
            raise GitHubUnavailable("GitHub returned an unexpected response") from exc

    @staticmethod
    def _validate(model: type[GitHubRepositoryDto] | type[GitHubCommunityProfileDto], payload: object):
        try:
            return model.model_validate(payload)
        except (ValueError, ValidationError) as exc:
            raise GitHubUnavailable("GitHub returned an unexpected response") from exc

    @staticmethod
    def _validate_list(model: type, payload: object) -> list:
        if not isinstance(payload, list):
            raise GitHubUnavailable("GitHub returned an unexpected response")
        try:
            return [model.model_validate(item) for item in payload]
        except (ValueError, ValidationError) as exc:
            raise GitHubUnavailable("GitHub returned an unexpected response") from exc
