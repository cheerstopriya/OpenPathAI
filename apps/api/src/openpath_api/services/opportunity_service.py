"""Use case for finding safe, evidence-backed contribution opportunities."""

import asyncio
from datetime import UTC, datetime

from openpath_api.domain.opportunities.ranking import rank_opportunities
from openpath_api.domain.repositories.reference import RepositoryReference
from openpath_api.integrations.github.client import GitHubClient
from openpath_api.schemas.opportunity import OpportunityListResponse, OpportunityResponse


class OpportunityService:
    def __init__(self, github_client: GitHubClient) -> None:
        self._github_client = github_client

    async def find(self, repository_url: str) -> OpportunityListResponse:
        reference = RepositoryReference.from_github_url(repository_url)
        repository, issues = await asyncio.gather(
            self._github_client.get_repository(reference),
            self._github_client.list_open_issues(reference, limit=30),
        )
        ranked = rank_opportunities(issues, evaluated_at=datetime.now(UTC))
        return OpportunityListResponse(
            repository_full_name=repository.full_name,
            sample_size=len(issues),
            opportunities=[
                OpportunityResponse(
                    number=item.issue.number,
                    title=item.issue.title,
                    html_url=item.issue.html_url,
                    labels=[label.name for label in item.issue.labels],
                    updated_at=item.issue.updated_at,
                    fit_score=item.fit_score,
                    reasons=list(item.reasons),
                )
                for item in ranked
            ],
            warning=None if ranked else "No unassigned issues were found in the sampled results.",
        )
