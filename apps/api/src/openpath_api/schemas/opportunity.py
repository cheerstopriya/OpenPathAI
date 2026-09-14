"""Public API contracts for contribution opportunities."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OpportunityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    repository_url: str = Field(min_length=1, max_length=300)


class OpportunityResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    number: int
    title: str
    html_url: str
    labels: list[str]
    updated_at: datetime
    fit_score: int = Field(ge=0, le=100)
    reasons: list[str]


class OpportunityListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    repository_full_name: str
    sample_size: int
    opportunities: list[OpportunityResponse]
    warning: str | None = None
