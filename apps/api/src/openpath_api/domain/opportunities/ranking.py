"""Explainable, deterministic ranking for unassigned open GitHub issues."""

from dataclasses import dataclass
from datetime import datetime

from openpath_api.domain.readiness.scoring import BEGINNER_LABELS
from openpath_api.integrations.github.models import GitHubIssueDto


@dataclass(frozen=True)
class RankedOpportunity:
    issue: GitHubIssueDto
    fit_score: int
    reasons: tuple[str, ...]


def rank_opportunities(
    issues: list[GitHubIssueDto], *, evaluated_at: datetime, limit: int = 10
) -> tuple[RankedOpportunity, ...]:
    candidates: list[RankedOpportunity] = []
    for issue in issues:
        if issue.pull_request is not None or issue.assignee is not None:
            continue
        labels = {label.name.casefold() for label in issue.labels}
        score = 25
        reasons = ["Unassigned, so it is more likely to be available."]
        if labels & BEGINNER_LABELS:
            score += 50
            reasons.append("Has a recognized beginner-friendly label.")
        age_days = max(0, (evaluated_at - issue.updated_at).days)
        if age_days <= 7:
            score += 15
            reasons.append(f"Updated recently ({age_days} days ago).")
        if len(issue.title.strip()) >= 20:
            score += 10
            reasons.append("Title provides useful initial context.")
        candidates.append(RankedOpportunity(issue=issue, fit_score=score, reasons=tuple(reasons)))
    return tuple(sorted(candidates, key=lambda item: (-item.fit_score, -item.issue.updated_at.timestamp()))[:limit])
