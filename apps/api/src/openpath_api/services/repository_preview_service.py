"""Use case for retrieving a safe public repository summary."""

from openpath_api.domain.repositories.reference import RepositoryReference
from openpath_api.integrations.github.client import GitHubClient
from openpath_api.schemas.repository import RepositoryPreviewResponse


class RepositoryPreviewService:
    def __init__(self, github_client: GitHubClient) -> None:
        self._github_client = github_client

    async def preview(self, repository_url: str) -> RepositoryPreviewResponse:
        reference = RepositoryReference.from_github_url(repository_url)
        repository = await self._github_client.get_repository(reference)

        return RepositoryPreviewResponse(
            owner=repository.owner.login,
            name=repository.name,
            full_name=repository.full_name,
            description=repository.description,
            html_url=repository.html_url,
            primary_language=repository.language,
            stars=repository.stargazers_count,
            forks=repository.forks_count,
            default_branch=repository.default_branch,
            archived=repository.archived,
            disabled=repository.disabled,
            visibility=repository.visibility,
            topics=repository.topics,
            license_spdx=repository.license.spdx_id if repository.license else None,
            pushed_at=repository.pushed_at,
        )
