"""Tests for bounded and parallel readiness evidence collection."""

import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT / "src"))

from openpath_api.domain.repositories.reference import RepositoryReference  # noqa: E402
from openpath_api.integrations.github.models import (  # noqa: E402
    GitHubCommunityProfileDto,
    GitHubIssueDto,
    GitHubOwnerDto,
    GitHubPullRequestDto,
    GitHubPullRequestReviewDto,
    GitHubRepositoryDto,
)
from openpath_api.services.readiness_evidence_service import (  # noqa: E402
    OPEN_ISSUE_SAMPLE_SIZE,
    PULL_REQUEST_SAMPLE_SIZE,
    REVIEWS_PER_PULL_REQUEST,
    ReadinessEvidenceService,
)


class ReadinessEvidenceServiceTest(unittest.IsolatedAsyncioTestCase):
    async def test_collects_bounded_evidence_and_excludes_prs_from_true_issues(self) -> None:
        now = datetime(2026, 8, 24, tzinfo=UTC)
        reference = RepositoryReference(owner="angular", name="angular")
        pull_request = GitHubPullRequestDto(
            number=42,
            html_url="https://github.com/angular/angular/pull/42",
            state="closed",
            created_at=now,
            closed_at=now,
            merged_at=now,
            user=GitHubOwnerDto(login="contributor"),
        )
        issue_payload = {
            "number": 7,
            "html_url": "https://github.com/angular/angular/issues/7",
            "title": "Starter issue",
            "created_at": now,
            "updated_at": now,
        }
        github_client = AsyncMock()
        github_client.get_repository.return_value = GitHubRepositoryDto(
            owner={"login": "angular"},
            name="angular",
            full_name="angular/angular",
            html_url="https://github.com/angular/angular",
            stargazers_count=1,
            forks_count=1,
            default_branch="main",
            archived=False,
            disabled=False,
            visibility="public",
            topics=[],
        )
        github_client.get_community_profile.return_value = GitHubCommunityProfileDto(
            health_percentage=80,
            files={},
        )
        github_client.list_pull_requests.return_value = [pull_request]
        github_client.list_pull_request_reviews.return_value = [
            GitHubPullRequestReviewDto(id=1, state="APPROVED", submitted_at=now)
        ]
        github_client.list_open_issues.return_value = [
            GitHubIssueDto.model_validate(issue_payload),
            GitHubIssueDto.model_validate({**issue_payload, "number": 8, "pull_request": {}}),
        ]

        evidence = await ReadinessEvidenceService(github_client).collect(reference)

        self.assertEqual(len(evidence.pull_requests), 1)
        self.assertEqual(len(evidence.pull_requests[0].reviews), 1)
        self.assertEqual([issue.number for issue in evidence.true_open_issues], [7])
        github_client.list_pull_requests.assert_awaited_once_with(
            reference, limit=PULL_REQUEST_SAMPLE_SIZE
        )
        github_client.list_open_issues.assert_awaited_once_with(
            reference, limit=OPEN_ISSUE_SAMPLE_SIZE
        )
        github_client.list_pull_request_reviews.assert_awaited_once_with(
            reference, 42, limit=REVIEWS_PER_PULL_REQUEST
        )


if __name__ == "__main__":
    unittest.main()
