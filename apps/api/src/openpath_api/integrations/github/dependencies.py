"""FastAPI dependency that owns the GitHub HTTP client's lifecycle."""

from collections.abc import AsyncIterator

import httpx
from fastapi import Depends

from openpath_api.config import Settings, get_settings
from openpath_api.integrations.github.client import GitHubClient


async def get_github_client(
    settings: Settings = Depends(get_settings),
) -> AsyncIterator[GitHubClient]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": settings.github_api_version,
        "User-Agent": "OpenPathAI/0.1",
    }
    if settings.github_token is not None and settings.github_token.get_secret_value():
        headers["Authorization"] = f"Bearer {settings.github_token.get_secret_value()}"

    async with httpx.AsyncClient(
        base_url="https://api.github.com",
        headers=headers,
        timeout=httpx.Timeout(settings.github_timeout_seconds),
        follow_redirects=False,
    ) as http_client:
        yield GitHubClient(http_client)
