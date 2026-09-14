"""Bounded, read-only collection of repository readiness evidence."""

import asyncio

from openpath_api.domain.readiness.evidence import (
    PullRequestEvidence,
    RepositoryReadinessEvidence,
)
from openpath_api.domain.repositories.reference import RepositoryReference
from openpath_api.integrations.github.client import GitHubClient

PULL_REQUEST_SAMPLE_SIZE = 10
REVIEWS_PER_PULL_REQUEST = 20
OPEN_ISSUE_SAMPLE_SIZE = 30


class ReadinessEvidenceService:
    def __init__(self, github_client: GitHubClient) -> None:
        self._github_client = github_client

    async def collect(
        self, reference: RepositoryReference
    ) -> RepositoryReadinessEvidence:
        repository, community_profile, pull_requests, open_issues = await asyncio.gather(
            self._github_client.get_repository(reference),
            self._github_client.get_community_profile(reference),
            self._github_client.list_pull_requests(
                reference, limit=PULL_REQUEST_SAMPLE_SIZE
            ),
            self._github_client.list_open_issues(
                reference, limit=OPEN_ISSUE_SAMPLE_SIZE
            ),
        )

        review_lists = await asyncio.gather(
            *(
                self._github_client.list_pull_request_reviews(
                    reference,
                    pull_request.number,
                    limit=REVIEWS_PER_PULL_REQUEST,
                )
                for pull_request in pull_requests
            )
        )
        pull_request_evidence = tuple(
            PullRequestEvidence(pull_request=pull_request, reviews=tuple(reviews))
            for pull_request, reviews in zip(pull_requests, review_lists, strict=True)
        )

        return RepositoryReadinessEvidence(
            repository=repository,
            community_profile=community_profile,
            pull_requests=pull_request_evidence,
            open_issues=tuple(open_issues),
        )
