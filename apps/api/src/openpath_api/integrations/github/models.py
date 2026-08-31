"""Data-transfer objects matching the GitHub REST API response."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GitHubOwnerDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    login: str


class GitHubLicenseDto(BaseModel):
    model_config = ConfigDict(extra="ignore")

    spdx_id: str | None = None


class GitHubRepositoryDto(BaseModel):
    """Only fields OpenPath currently needs from GitHub's larger response."""

    model_config = ConfigDict(extra="ignore")

    owner: GitHubOwnerDto
    name: str
    full_name: str
    description: str | None = None
    html_url: str
    language: str | None = None
    stargazers_count: int
    forks_count: int
    default_branch: str
    archived: bool
    disabled: bool
    visibility: str
    topics: list[str]
    license: GitHubLicenseDto | None = None
    pushed_at: datetime | None = None
