"""Public API contracts for repository contribution-readiness analysis."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ConfidenceValue = Literal["low", "medium", "high"]


class RepositoryReadinessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repository_url: str = Field(min_length=1, max_length=300)


class ReadinessDimensionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    title: str
    weight: int = Field(ge=0, le=100)
    score: int | None = Field(default=None, ge=0, le=100)
    confidence: ConfidenceValue
    sample_size: int = Field(ge=0)
    observations: list[str]
    evidence_urls: list[str]
    warnings: list[str]


class RepositoryReadinessResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repository_full_name: str
    repository_html_url: str
    evaluated_at: datetime
    overall_score: int | None = Field(default=None, ge=0, le=100)
    coverage_percentage: int = Field(ge=0, le=100)
    confidence: ConfidenceValue
    formula_version: str
    dimensions: list[ReadinessDimensionResponse]
    warnings: list[str]
