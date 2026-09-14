"""Versioned, deterministic repository contribution-readiness scoring."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from statistics import median

from openpath_api.domain.readiness.evidence import RepositoryReadinessEvidence

FORMULA_VERSION = "1.0.0"
BEGINNER_LABELS = {
    "beginner",
    "easy",
    "first-timers-only",
    "good first issue",
    "good-first-issue",
    "help wanted",
    "starter",
}


class Confidence(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class DimensionScore:
    key: str
    title: str
    weight: int
    score: int | None
    confidence: Confidence
    sample_size: int
    observations: tuple[str, ...]
    evidence_urls: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReadinessScore:
    overall_score: int | None
    coverage_percentage: int
    confidence: Confidence
    formula_version: str
    dimensions: tuple[DimensionScore, ...]
    warnings: tuple[str, ...] = ()


def calculate_readiness(
    evidence: RepositoryReadinessEvidence, *, evaluated_at: datetime
) -> ReadinessScore:
    dimensions = (
        _maintenance(evidence, evaluated_at),
        _documentation(evidence),
        _review_responsiveness(evidence),
        _contribution_outcomes(evidence),
        _beginner_issues(evidence),
        _community_participation(evidence),
    )
    available = tuple(item for item in dimensions if item.score is not None)
    available_weight = sum(item.weight for item in available)
    overall = (
        round(sum(item.score * item.weight for item in available) / available_weight)
        if available_weight
        else None
    )
    coverage = available_weight
    confidence = _overall_confidence(available, coverage)
    warnings: list[str] = []
    if coverage < 100:
        warnings.append(
            "Some dimensions lacked enough evidence; available weights were re-normalized."
        )
    if evidence.repository.archived or evidence.repository.disabled:
        warnings.append("This repository is archived or disabled and may not accept contributions.")

    return ReadinessScore(
        overall_score=overall,
        coverage_percentage=coverage,
        confidence=confidence,
        formula_version=FORMULA_VERSION,
        dimensions=dimensions,
        warnings=tuple(warnings),
    )


def _maintenance(
    evidence: RepositoryReadinessEvidence, evaluated_at: datetime
) -> DimensionScore:
    pushed_at = evidence.repository.pushed_at
    if pushed_at is None:
        return _missing("maintenance_activity", "Maintenance activity", 20, "Missing push date.")
    days = max(0, (evaluated_at - pushed_at).days)
    score = _threshold_score(days, ((30, 100), (90, 80), (180, 60), (365, 35)), 10)
    return DimensionScore(
        key="maintenance_activity",
        title="Maintenance activity",
        weight=20,
        score=score,
        confidence=Confidence.HIGH,
        sample_size=1,
        observations=(f"Last repository push was {days} days ago.",),
        evidence_urls=(evidence.repository.html_url,),
    )


def _documentation(evidence: RepositoryReadinessEvidence) -> DimensionScore:
    files = evidence.community_profile.files
    checks = {
        "README": files.readme,
        "CONTRIBUTING guide": files.contributing,
        "license": files.license,
        "code of conduct": files.code_of_conduct,
        "issue template": files.issue_template,
        "pull request template": files.pull_request_template,
    }
    present = tuple(name for name, value in checks.items() if value is not None)
    missing = tuple(name for name, value in checks.items() if value is None)
    score = round(len(present) / len(checks) * 100)
    observations = (
        f"Found {len(present)} of {len(checks)} newcomer-support files.",
        f"Present: {', '.join(present) if present else 'none'}.",
    )
    warnings = (f"Missing: {', '.join(missing)}.",) if missing else ()
    return DimensionScore(
        key="newcomer_documentation",
        title="Newcomer documentation",
        weight=20,
        score=score,
        confidence=Confidence.HIGH,
        sample_size=len(checks),
        observations=observations,
        evidence_urls=tuple(
            value.html_url for value in checks.values() if value is not None and value.html_url
        ),
        warnings=warnings,
    )


def _review_responsiveness(evidence: RepositoryReadinessEvidence) -> DimensionScore:
    response_hours: list[float] = []
    for item in evidence.pull_requests:
        submitted = [review.submitted_at for review in item.reviews if review.submitted_at]
        if submitted:
            response_hours.append(
                max(0, (min(submitted) - item.pull_request.created_at).total_seconds() / 3600)
            )
    if not response_hours:
        return _missing(
            "review_responsiveness",
            "Review responsiveness",
            20,
            "No submitted reviews were found in the sampled pull requests.",
        )
    hours = median(response_hours)
    score = _threshold_score(hours, ((24, 100), (72, 80), (168, 60), (336, 35)), 10)
    return DimensionScore(
        key="review_responsiveness",
        title="Review responsiveness",
        weight=20,
        score=score,
        confidence=_sample_confidence(len(response_hours), medium=3, high=7),
        sample_size=len(response_hours),
        observations=(f"Median time to first submitted review was {hours:.1f} hours.",),
        evidence_urls=tuple(
            item.pull_request.html_url
            for item in evidence.pull_requests
            if any(review.submitted_at for review in item.reviews)
        ),
        warnings=_sample_warning(len(response_hours), 7, "reviewed pull requests"),
    )


def _contribution_outcomes(evidence: RepositoryReadinessEvidence) -> DimensionScore:
    closed = [item.pull_request for item in evidence.pull_requests if item.pull_request.closed_at]
    if not closed:
        return _missing(
            "contribution_outcomes",
            "Contribution outcomes",
            15,
            "No closed pull requests were found in the sample.",
        )
    merged = sum(item.merged_at is not None for item in closed)
    ratio = merged / len(closed)
    score = round(ratio * 100)
    return DimensionScore(
        key="contribution_outcomes",
        title="Contribution outcomes",
        weight=15,
        score=score,
        confidence=_sample_confidence(len(closed), medium=3, high=7),
        sample_size=len(closed),
        observations=(f"{merged} of {len(closed)} sampled closed pull requests were merged.",),
        evidence_urls=tuple(item.html_url for item in closed),
        warnings=_sample_warning(len(closed), 7, "closed pull requests"),
    )


def _beginner_issues(evidence: RepositoryReadinessEvidence) -> DimensionScore:
    issues = evidence.true_open_issues
    beginner = [
        issue
        for issue in issues
        if {label.name.casefold() for label in issue.labels} & BEGINNER_LABELS
    ]
    unassigned = sum(issue.assignee is None for issue in beginner)
    score = _threshold_score(unassigned, ((0, 0), (1, 50), (2, 75), (5, 100)), 100)
    return DimensionScore(
        key="beginner_issue_availability",
        title="Beginner issue availability",
        weight=15,
        score=score,
        confidence=_sample_confidence(len(issues), medium=10, high=25),
        sample_size=len(issues),
        observations=(
            f"Found {len(beginner)} beginner-labelled issues; {unassigned} were unassigned.",
            f"Inspected {len(issues)} true issues after excluding pull requests.",
        ),
        evidence_urls=tuple(issue.html_url for issue in beginner),
        warnings=_sample_warning(len(issues), 25, "open issues"),
    )


def _community_participation(evidence: RepositoryReadinessEvidence) -> DimensionScore:
    participants = {
        item.pull_request.user.login.casefold() for item in evidence.pull_requests
    }
    participants.update(
        review.user.login.casefold()
        for item in evidence.pull_requests
        for review in item.reviews
        if review.user is not None
    )
    count = len(participants)
    if not evidence.pull_requests:
        return _missing(
            "community_participation",
            "Community participation",
            10,
            "No pull requests were found in the sample.",
        )
    score = _threshold_score(count, ((1, 20), (2, 40), (4, 70), (7, 100)), 100)
    return DimensionScore(
        key="community_participation",
        title="Community participation",
        weight=10,
        score=score,
        confidence=_sample_confidence(len(evidence.pull_requests), medium=3, high=7),
        sample_size=len(evidence.pull_requests),
        observations=(f"Observed {count} distinct PR authors and reviewers in the sample.",),
        evidence_urls=tuple(
            item.pull_request.html_url for item in evidence.pull_requests
        ),
        warnings=_sample_warning(len(evidence.pull_requests), 7, "pull requests"),
    )


def _missing(key: str, title: str, weight: int, warning: str) -> DimensionScore:
    return DimensionScore(
        key=key,
        title=title,
        weight=weight,
        score=None,
        confidence=Confidence.LOW,
        sample_size=0,
        observations=(),
        warnings=(warning,),
    )


def _threshold_score(value: float, thresholds: tuple[tuple[float, int], ...], fallback: int) -> int:
    for upper_bound, score in thresholds:
        if value <= upper_bound:
            return score
    return fallback


def _sample_confidence(size: int, *, medium: int, high: int) -> Confidence:
    if size >= high:
        return Confidence.HIGH
    if size >= medium:
        return Confidence.MEDIUM
    return Confidence.LOW


def _sample_warning(size: int, target: int, label: str) -> tuple[str, ...]:
    if size >= target:
        return ()
    return (f"Low sample size: observed {size} of the target {target} {label}.",)


def _overall_confidence(
    available: tuple[DimensionScore, ...], coverage: int
) -> Confidence:
    if coverage < 70 or not available:
        return Confidence.LOW
    confidence_value = {Confidence.LOW: 1, Confidence.MEDIUM: 2, Confidence.HIGH: 3}
    average = sum(confidence_value[item.confidence] for item in available) / len(available)
    if coverage == 100 and average >= 2.5:
        return Confidence.HIGH
    if average >= 1.75:
        return Confidence.MEDIUM
    return Confidence.LOW
