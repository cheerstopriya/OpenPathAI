"""Deterministic tests for the versioned readiness formula."""

import sys
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT / "src"))

from openpath_api.domain.readiness.evidence import (  # noqa: E402
    PullRequestEvidence,
    RepositoryReadinessEvidence,
)
from openpath_api.domain.readiness.scoring import (  # noqa: E402
    FORMULA_VERSION,
    Confidence,
    calculate_readiness,
)
from openpath_api.integrations.github.models import (  # noqa: E402
    GitHubCommunityProfileDto,
    GitHubIssueDto,
    GitHubOwnerDto,
    GitHubPullRequestDto,
    GitHubPullRequestReviewDto,
    GitHubRepositoryDto,
)

NOW = datetime(2026, 9, 1, tzinfo=UTC)


def build_evidence(*, with_activity: bool = True) -> RepositoryReadinessEvidence:
    owner = GitHubOwnerDto(login="contributor")
    pulls: tuple[PullRequestEvidence, ...] = ()
    issues: tuple[GitHubIssueDto, ...] = ()
    if with_activity:
        pull = GitHubPullRequestDto(
            number=1,
            html_url="https://github.com/example/project/pull/1",
            state="closed",
            created_at=NOW - timedelta(days=10),
            closed_at=NOW - timedelta(days=8),
            merged_at=NOW - timedelta(days=8),
            user=owner,
        )
        review = GitHubPullRequestReviewDto(
            id=1,
            state="APPROVED",
            submitted_at=pull.created_at + timedelta(hours=12),
            user=GitHubOwnerDto(login="maintainer"),
        )
        pulls = (PullRequestEvidence(pull_request=pull, reviews=(review,)),)
        issues = (
            GitHubIssueDto(
                number=2,
                html_url="https://github.com/example/project/issues/2",
                title="Starter task",
                created_at=NOW - timedelta(days=3),
                updated_at=NOW,
                labels=[{"name": "good first issue"}],
            ),
        )
    return RepositoryReadinessEvidence(
        repository=GitHubRepositoryDto(
            owner={"login": "example"},
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
            pushed_at=NOW - timedelta(days=5),
        ),
        community_profile=GitHubCommunityProfileDto(
            health_percentage=100,
            files={
                "readme": {},
                "contributing": {},
                "license": {},
                "code_of_conduct": {},
                "issue_template": {},
                "pull_request_template": {},
            },
        ),
        pull_requests=pulls,
        open_issues=issues,
    )


class ReadinessScoringTest(unittest.TestCase):
    def test_produces_explainable_versioned_scores(self) -> None:
        result = calculate_readiness(build_evidence(), evaluated_at=NOW)

        self.assertEqual(result.formula_version, FORMULA_VERSION)
        self.assertEqual(result.coverage_percentage, 100)
        self.assertIsNotNone(result.overall_score)
        dimensions = {item.key: item for item in result.dimensions}
        self.assertEqual(dimensions["maintenance_activity"].score, 100)
        self.assertEqual(dimensions["newcomer_documentation"].score, 100)
        self.assertEqual(dimensions["review_responsiveness"].score, 100)
        self.assertEqual(dimensions["contribution_outcomes"].score, 100)
        self.assertEqual(dimensions["beginner_issue_availability"].score, 50)
        self.assertIn("12.0 hours", dimensions["review_responsiveness"].observations[0])

    def test_marks_missing_dimensions_instead_of_scoring_them_as_zero(self) -> None:
        result = calculate_readiness(build_evidence(with_activity=False), evaluated_at=NOW)

        self.assertEqual(result.coverage_percentage, 55)
        self.assertEqual(result.confidence, Confidence.LOW)
        self.assertEqual(len(result.warnings), 1)
        unavailable = [item for item in result.dimensions if item.score is None]
        self.assertEqual(len(unavailable), 3)
        self.assertTrue(all(item.confidence == Confidence.LOW for item in unavailable))

    def test_flags_archived_repository(self) -> None:
        evidence = build_evidence()
        evidence.repository.archived = True

        result = calculate_readiness(evidence, evaluated_at=NOW)

        self.assertTrue(any("archived" in warning for warning in result.warnings))


if __name__ == "__main__":
    unittest.main()
