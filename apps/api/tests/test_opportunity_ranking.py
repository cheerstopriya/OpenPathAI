import sys
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT / "src"))

from openpath_api.domain.opportunities.ranking import rank_opportunities  # noqa: E402
from openpath_api.integrations.github.models import GitHubIssueDto  # noqa: E402


class OpportunityRankingTest(unittest.TestCase):
    def test_prioritizes_unassigned_beginner_issue_and_excludes_pull_requests(self) -> None:
        now = datetime(2026, 9, 15, tzinfo=UTC)
        issue = {"html_url": "https://github.com/a/b/issues/1", "title": "Improve documentation for a new contributor", "created_at": now, "updated_at": now}
        ranked = rank_opportunities([
            GitHubIssueDto.model_validate({**issue, "number": 1, "labels": [{"name": "good first issue"}]}),
            GitHubIssueDto.model_validate({**issue, "number": 2, "pull_request": {}}),
            GitHubIssueDto.model_validate({**issue, "number": 3, "assignee": {"login": "someone"}}),
        ], evaluated_at=now + timedelta(days=1))
        self.assertEqual([item.issue.number for item in ranked], [1])
        self.assertEqual(ranked[0].fit_score, 100)


if __name__ == "__main__":
    unittest.main()
