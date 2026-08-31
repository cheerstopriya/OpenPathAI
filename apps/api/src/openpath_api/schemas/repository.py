"""Public API contracts for repository preview."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repository_url: str = Field(min_length=1, max_length=300)


class RepositoryPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    owner: str
    name: str
    full_name: str
    description: str | None
    html_url: str
    primary_language: str | None
    stars: int
    forks: int
    default_branch: str
    archived: bool
    disabled: bool
    visibility: str
    topics: list[str]
    license_spdx: str | None
    pushed_at: datetime | None
