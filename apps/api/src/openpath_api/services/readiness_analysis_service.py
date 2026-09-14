"""Application use case for contribution-readiness analysis."""

from datetime import UTC, datetime

from openpath_api.domain.readiness.scoring import calculate_readiness
from openpath_api.domain.repositories.reference import RepositoryReference
from openpath_api.integrations.github.client import GitHubClient
from openpath_api.schemas.readiness import (
    ReadinessDimensionResponse,
    RepositoryReadinessResponse,
)
from openpath_api.services.readiness_evidence_service import ReadinessEvidenceService


class ReadinessAnalysisService:
    def __init__(self, github_client: GitHubClient) -> None:
        self._evidence_service = ReadinessEvidenceService(github_client)

    async def analyze(
        self, repository_url: str, *, evaluated_at: datetime | None = None
    ) -> RepositoryReadinessResponse:
        reference = RepositoryReference.from_github_url(repository_url)
        timestamp = evaluated_at or datetime.now(UTC)
        evidence = await self._evidence_service.collect(reference)
        result = calculate_readiness(evidence, evaluated_at=timestamp)

        return RepositoryReadinessResponse(
            repository_full_name=evidence.repository.full_name,
            repository_html_url=evidence.repository.html_url,
            evaluated_at=timestamp,
            overall_score=result.overall_score,
            coverage_percentage=result.coverage_percentage,
            confidence=result.confidence.value,
            formula_version=result.formula_version,
            dimensions=[
                ReadinessDimensionResponse(
                    key=item.key,
                    title=item.title,
                    weight=item.weight,
                    score=item.score,
                    confidence=item.confidence.value,
                    sample_size=item.sample_size,
                    observations=list(item.observations),
                    evidence_urls=list(item.evidence_urls),
                    warnings=list(item.warnings),
                )
                for item in result.dimensions
            ],
            warnings=list(result.warnings),
        )
