"""Evidence collected before deterministic readiness scoring."""

from dataclasses import dataclass

from openpath_api.integrations.github.models import (
    GitHubCommunityProfileDto,
    GitHubIssueDto,
    GitHubPullRequestDto,
    GitHubPullRequestReviewDto,
    GitHubRepositoryDto,
)


@dataclass(frozen=True)
class PullRequestEvidence:
    pull_request: GitHubPullRequestDto
    reviews: tuple[GitHubPullRequestReviewDto, ...]


@dataclass(frozen=True)
class RepositoryReadinessEvidence:
    repository: GitHubRepositoryDto
    community_profile: GitHubCommunityProfileDto
    pull_requests: tuple[PullRequestEvidence, ...]
    open_issues: tuple[GitHubIssueDto, ...]

    @property
    def true_open_issues(self) -> tuple[GitHubIssueDto, ...]:
        """GitHub's issues endpoint also returns PRs; exclude those entries."""

        return tuple(issue for issue in self.open_issues if issue.pull_request is None)
